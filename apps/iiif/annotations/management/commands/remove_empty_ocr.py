from django.core.management.base import BaseCommand
from apps.iiif.annotations.models import Annotation

class Command(BaseCommand):
    help = 'Removes OCR annotations with no content.'

    def handle(self, *args, **options):
        for ocr in Annotation.objects.filter(resource_type=Annotation.OCR):
            if not ocr.content or ocr.content.isspace() or ocr.content is None:
                ocr.delete()
        
        self.stdout.write(self.style.SUCCESS('Empty OCR annotations have been removed'))
