"""Django Models for Readux"""
import json
import re
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from apps.iiif.annotations.models import AbstractAnnotation, Annotation
from apps.iiif.canvases.models import Canvas
from apps.iiif.manifests.documents import ManifestDocument
class TaggedUserAnnotations(TaggedItemBase):
    """Model for tagging :class:`UserAnnotation`s using Django Taggit."""
    content_object = models.ForeignKey('UserAnnotation', on_delete=models.CASCADE)

class UserAnnotation(AbstractAnnotation):
    """Model for User Annotations."""
    COMMENTING = 'oa:commenting'
    PAINTING = 'sc:painting'
    TAGGING = '%s,oa:tagging' % COMMENTING
    MOTIVATION_CHOICES = (
        (COMMENTING, 'commenting'),
        (PAINTING, 'painting'),
        (TAGGING, 'tagging and commenting')
    )

    start_selector = models.ForeignKey(
        Annotation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='start_selector',
        default=None
    )
    end_selector = models.ForeignKey(
        Annotation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='end_selector',
        default=None
    )
    start_offset = models.IntegerField(null=True, blank=True, default=None)
    end_offset = models.IntegerField(null=True, blank=True, default=None)
    tags = TaggableManager(through=TaggedUserAnnotations)

    @property
    def item(self):
        if self.__is_text_annotation():
            return self.__text_anno_item()
        elif self.__is_svg_annotation():
            return self.__svg_anno_item()
        else:
            return None

    @property
    def tag_list(self):
        if self.tags.exists():
            return [tag.name for tag in self.tags.all()]
        else:
            return []

    def save(self, *args, **kwargs):
        if self.canvas:
            index = ManifestDocument()
            index.update(self.canvas.manifest, True, 'index')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.canvas:
            index = ManifestDocument()
            index.update(self.canvas.manifest, True, 'delete')
        super().delete(*args, **kwargs)

    def update(self, attrs=None, tags=None):
        """Method to update an annotation object with a dict of attributes and a list of tags

        :param attrs: _description_, defaults to None
        :type attrs: dict, optional
        :param tags: _description_, defaults to None
        :type tags: list, optional
        """
        if isinstance(attrs, dict):
            for attr, value in attrs.items():
                setattr(self, attr, value)


        if isinstance(tags, list):
            self.tags.clear()
            for tag in tags:
                self.tags.add(tag)

        self.save()

    def parse_mirador_annotation(self):
        self.motivation = AbstractAnnotation.OA_COMMENTING

        if type(self.oa_annotation) == str:
            self.oa_annotation = json.loads(self.oa_annotation)

        if isinstance(self.oa_annotation['on'], list):
            anno_on = self.oa_annotation['on'][0]
        elif isinstance(self.oa_annotation['on'], dict):
            anno_on = self.oa_annotation['on']

        if self.canvas == None:
            self.canvas = Canvas.objects.get(pid=anno_on['full'].split('/')[-1])

        mirador_item = anno_on['selector']['item']

        if mirador_item['@type'] == 'oa:SvgSelector':
            self.svg = mirador_item['value']
            self.__set_xywh_svg_anno()

        elif mirador_item['@type'] == 'RangeSelector':
            self.start_selector = Annotation.objects.get(
                pk=mirador_item['startSelector']['value'].split("'")[1]
            )
            self.end_selector = Annotation.objects.get(
                pk=mirador_item['endSelector']['value'].split("'")[1]
            )
            self.start_offset = mirador_item['startSelector']['refinedBy']['start']
            self.end_offset = mirador_item['endSelector']['refinedBy']['end']
            self.__set_xywh_text_anno()

        if isinstance(self.oa_annotation['resource'], dict):
            self.content = self.oa_annotation['resource']['chars']
            self.resource_type = self.oa_annotation['resource']['@type']
        elif isinstance(self.oa_annotation['resource'], list) and len(self.oa_annotation['resource']) == 1:
            self.content = self.oa_annotation['resource'][0]['chars']
            self.resource_type = self.oa_annotation['resource'][0]['@type']
            # Assume all tags have been removed.
            if self.tags.exists():
                self.tags.clear()
        elif (
                isinstance(self.oa_annotation['resource'], list) and
                len(self.oa_annotation['resource']) > 1
        ):
            # Assume tagging
            self.motivation = self.TAGGING
            text = [res for res in self.oa_annotation['resource'] if res['@type'] == 'dctypes:Text']
            self.content = text[0]['chars']

        # Replace the ID given by Mirador with the Readux given ID
        if 'stylesheet' in self.oa_annotation:
            uuid_pattern = re.compile(
                r'[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}'
            )
            self.style = uuid_pattern.sub(str(self.id), self.oa_annotation['stylesheet']['value'])

        return True

    def __is_text_annotation(self):
        """Check if annotation is for text.

        :return: True if annotation is for text.
        :rtype: bool
        """
        return all([
            isinstance(self.end_offset, int),
            isinstance(self.start_offset, int),
            isinstance(self.start_selector, Annotation),
            isinstance(self.end_selector, Annotation)
        ])

    def __is_svg_annotation(self):
        """Check if annotation is for image region.

        :return: True if annotation is for image region.
        :rtype: bool
        """
        return self.svg is not None

    # pylint: disable = invalid-name
    def __set_xywh_text_anno(self):
        start_position = self.start_selector.order
        end_position = self.end_selector.order
        text = Annotation.objects.filter(
            canvas=self.canvas,
            order__lt=end_position,
            order__gte=start_position
        ).order_by('order')
        self.x = min(text.values_list('x', flat=True))
        self.y = max(text.values_list('y', flat=True))
        self.h = max(text.values_list('h', flat=True))
        self.w = text.last().x + text.last().w - self.x
    # pylint: enable = invalid-name

    def __text_anno_item(self):
        return dict({
            "@type": "RangeSelector",
            "startSelector": {
                "@type": "XPathSelector",
                "value": "//*[@id='%s']" % str(self.start_selector.pk),
                "refinedBy" : {
                    "@type": "TextPositionSelector",
                    "start": self.start_offset
                }
            },
            "endSelector": {
                "@type": "XPathSelector",
                "value": "//*[@id='%s']" % str(self.end_selector.pk),
                "refinedBy" : {
                    "@type": "TextPositionSelector",
                    "end": self.end_offset
                }
            }
        })

    def __svg_anno_item(self):
        return dict({
            "@type": "oa:SvgSelector",
            "value": self.svg,
            "@type": "oa:Choice",
            "default": {
                "@type": "oa:FragmentSelector",
                "value": "xywh=%s,%s,%s,%s" % (str(self.x), str(self.y), str(self.w), str(self.h))
            }
        })

    def __set_xywh_svg_anno(self):
        dimensions = None
        if 'default' in self.oa_annotation['on'][0]['selector'].keys():
            dimensions = self.oa_annotation['on'][0]['selector']['default']['value'].split('=')[-1].split(',') # pylint: disable = line-too-long
        if dimensions is not None:
            self.x = dimensions[0]
            self.y = dimensions[1]
            self.w = dimensions[2]
            self.h = dimensions[3]

# TODO: Override the save method and move this there.
@receiver(signals.pre_save, sender=UserAnnotation)
def parse_payload(sender, instance, **kwargs):  # pylint: disable=unused-argument
    # if service.validate_oa_annotation(instance.oa_annotation):
    if isinstance(instance.oa_annotation, dict) and 'on' not in instance.oa_annotation.keys():
        return None
    instance.parse_mirador_annotation()

@receiver(signals.post_save, sender=UserAnnotation)
def set_tags(sender, instance, **kwargs):
    """
    Finds tags in the oa_annotation and applies them to
    the annotation.
    """
    if instance.motivation == sender.TAGGING:
        incoming_tags = []
        # Get the tags from the incoming annotation.
        tags = [res for res in instance.oa_annotation['resource'] if res['@type'] == 'oa:Tag']
        for tag in tags:
            # Add the tag to the annotation
            instance.tags.add(tag['chars'])
            # Make a list of incoming tags to compare with list of saved tags.
            incoming_tags.append(tag['chars'])

        # Check if any tags have been removed
        if len(instance.tag_list) > 0:
            for existing_tag in instance.tag_list:
                if existing_tag not in incoming_tags:
                    instance.tags.remove(existing_tag)
