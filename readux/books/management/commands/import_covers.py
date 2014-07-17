import logging
from optparse import make_option

from django.core.management.base import BaseCommand

from readux.books.models import Volume
from readux.books.management.page_import import BasePageImport


logger = logging.getLogger(__name__)


class Command(BasePageImport):
    '''Identify and ingest cover images for Volume objects in Fedora.
Takes an optional list of pids; otherwise, looks for all Volume objects in
the configured fedora instance.'''
    help = __doc__

    option_list = BaseCommand.option_list + (
        make_option('--dry-run', '-n',
            action='store_true',
            default=False,
            help='Don\'t make any changes; just report on what would be done'),
        )

    v_normal = 1

    def handle(self, *pids, **options):
        self.setup(**options)

        # if pids are specified on command line, only process those objects
        if pids:
            objs = [self.repo.get_object(pid, type=Volume) for pid in pids]

        # otherwise, look for all volume objects in fedora
        else:
            objs = self.repo.get_objects_with_cmodel(Volume.VOLUME_CONTENT_MODEL,
                                                type=Volume)

        for vol in objs:
            self.stats['vols'] += 1
            # if object does not exist or cannot be accessed in fedora, skip it
            if not self.is_usable_volume(vol):
                continue

            # if volume already has a cover, don't re-ingest
            if vol.primary_image:
                self.stats['skipped'] += 1
                if self.verbosity >= self.v_normal:
                    self.stdout.write('%s already has a cover image %s' % \
                        (vol.pid, vol.primary_image.pid))
                continue

            images, vol_info = self.find_page_images(vol)
            # if either images or volume info were not found, skip
            if not images or not vol_info:
                self.stats['skipped'] += 1   # or error?
                continue

            # TODO: could we also use this logic to calculate and store
            # what page the PDF should be opened to?

            # cover detection (currently first non-blank page)
            coverfile, coverindex = self.identify_cover(images)

            # if a non-blank page was not found in the first 5 pages,
            # report as an error and skip this volume
            if coverindex is None:
                if self.verbosity >= self.v_normal:
                    self.stdout.write('Error: could not identify cover page in first %d images; skipping' % \
                                      self.cover_range)
                continue        # skip to next volume

            # create the page image object and associate with volume
            self.ingest_page(coverfile, vol, vol_info, cover=True)


        if self.verbosity >= self.v_normal:
            self.stdout.write('\n%(vols)d volume(s); %(errors)d error(s), %(skipped)d skipped, %(updated)d updated' % \
                self.stats)





