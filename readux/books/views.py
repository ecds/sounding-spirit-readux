from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.urlresolvers import reverse
from django.core.servers.basehttp import FileWrapper
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpResponse, HttpResponseNotFound, \
    HttpResponsePermanentRedirect, StreamingHttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.http import condition, require_http_methods, \
   last_modified
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import ListView, DetailView, View
from django.views.generic.base import RedirectView
import json
from urllib import urlencode
import os
import requests
import logging

from eulfedora.server import Repository, TypeInferringRepository, RequestFailed
from eulfedora.views import raw_datastream, RawDatastreamView

from readux.books.models import Volume, SolrVolume, Page, VolumeV1_0, \
    PageV1_1, SolrPage
from readux.books.forms import BookSearch
from readux.books import view_helpers, annotate, export
from readux.utils import solr_interface, absolutize_url
from readux.views import VaryOnCookieMixin


logger = logging.getLogger(__name__)


class VolumeSearch(ListView):
    '''Search across all volumes.'''

    model = Volume
    template_name = 'books/volume_search.html'
    paginate_by = 10
    context_object_name = 'items'

    display_mode = 'list'
    display_filters = []
    sort_options = ['relevance', 'title', 'date added']

    @method_decorator(last_modified(view_helpers.volumes_modified))
    def dispatch(self, *args, **kwargs):
        return super(VolumeSearch, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        self.form = BookSearch(self.request.GET)

        # sort: currently supports relevance, title, or date added
        self.sort = self.request.GET.get('sort', None)

        if self.form.is_valid():
            # get list of keywords and phrases
            terms = self.form.search_terms()
            solr = solr_interface()
            # generate queries text and boost-field queries
            text_query = solr.Q()
            author_query = solr.Q()
            title_query = solr.Q()
            for t in terms:
                text_query |= solr.Q(t)
                author_query |= solr.Q(creator=t)
                title_query |= solr.Q(title=t)

            q = solr.query().filter(content_model=Volume.VOLUME_CMODEL_PATTERN) \
                    .query(text_query | author_query**3 | title_query**3) \
                    .field_limit(SolrVolume.necessary_fields, score=True)  \
                    .results_as(SolrVolume)

            if self.sort not in self.sort_options:
                # by default, sort by relevance score
                self.sort = 'relevance'
            if self.sort == 'relevance':
                q = q.sort_by('-score')
            elif self.sort == 'title':
                # sort by title and then by label so multi-volume works should group
                # together in the correct order
                q = q.sort_by('title_exact').sort_by('label')
            elif self.sort == 'date added':
                q = q.sort_by('-created')

            url_params = self.request.GET.copy()

            # don't need to facet on collection if we are already filtered on collection
            if 'collection' not in self.request.GET:
                q = q.facet_by('collection_label_facet', sort='index', mincount=1)

            self.display_filters = []
            if 'collection' in self.request.GET:
                filter_val = self.request.GET['collection']
                # filter the solr query based on the requested collection
                q = q.query(collection_label='"%s"' % filter_val)
                # generate link to remove the facet
                unfacet_urlopts = url_params.copy()
                del unfacet_urlopts['collection']
                self.display_filters.append(('collection', filter_val,
                                        unfacet_urlopts.urlencode()))

            # active filter - only show volumes with pages loaded
            if 'read_online' in self.request.GET and self.request.GET['read_online']:
                q = q.query(page_count__gte=2)
                unfacet_urlopts = url_params.copy()
                del unfacet_urlopts['read_online']
                self.display_filters.append(('Read online', '',
                                        unfacet_urlopts.urlencode()))
            else:
                # generate a facet count for books with pages loaded
                q = q.facet_query(page_count__gte=2)

            return q

        else:
            # empty 'queryset' result required by view methods
            return []


    def get_context_data(self):
        context_data = super(VolumeSearch, self).get_context_data()

        url_params = self.request.GET.copy()
        sort_url_params = self.request.GET.copy()
        if 'sort' in sort_url_params:
            del sort_url_params['sort']

        context_data.update({
            'form': self.form,
            'url_params': urlencode(url_params),
            'mode': self.display_mode,  # list / cover view
            'current_url_params': urlencode(self.request.GET.copy()),
            'sort': self.sort,
            'sort_options': self.sort_options,
            'sort_url_params': urlencode(sort_url_params),
        })

        # get facets and annotations IF there are are any search results
        if context_data['object_list']:
            # adjust facets as returned from solr for display
            facet_counts = context_data['object_list'].facet_counts
            facets = {}
            collections = facet_counts.facet_fields.get('collection_label_facet', [])
            # only include collections in facet if there are any
            if collections:
                facets['collection'] = collections
            if facet_counts.facet_queries:
                # number of volumes with pages loaded;
                # facet query is a list of tuple; second value is the count
                pages_loaded = facet_counts.facet_queries[0][1]
                # only display if it is a facet, i.e. not all volumes
                # in the result set have pages loaded
                if pages_loaded < context_data['paginator'].count:
                    facets['pages_loaded'] = facet_counts.facet_queries[0][1]

            # generate list for display and removal of active filters
            q = self.get_queryset()
            annotated_volumes = {}
            if context_data['paginator'].count and self.request.user.is_authenticated():
                notes = Volume.volume_annotation_count(self.request.user)
                domain = get_current_site(self.request).domain.rstrip('/')
                if not domain.startswith('http'):
                    domain = 'http://' + domain
                annotated_volumes = dict([(k.replace(domain, ''), v)
                                   for k, v in notes.iteritems()])

            context_data.update({
                'facets': facets,  # available facets
                'filters': self.display_filters,  # active filters
                'annotated_volumes': annotated_volumes
            })

        return context_data


class VolumeCoverSearch(VolumeSearch):
    display_mode = 'covers'


class VolumeDetail(DetailView, VaryOnCookieMixin):
    ''' Landing page for a single :class:`~readux.books.models.Volume`.

    If keyword search terms are specified, searches within the book and
    finds matching pages.
    '''
    model = Volume
    template_name = 'books/volume_detail.html'
    search_template_name = 'books/volume_pages_search.html'
    context_object_name = 'vol'

    @method_decorator(last_modified(view_helpers.volume_modified))
    def dispatch(self, *args, **kwargs):
        return super(VolumeDetail, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        # kwargs are set based on configured url pattern
        pid = self.kwargs['pid']
        repo = Repository(request=self.request)
        vol = repo.get_object(pid, type=Volume)
        if not vol.exists or not vol.is_a_volume:
            raise Http404
        return vol

    def get_template_names(self):
        # search results require a different template
        if self.form.is_valid():
            return self.search_template_name
        return self.template_name

    def get_context_data(self, **kwargs):
        context_data = super(VolumeDetail, self).get_context_data()
        # sort: currently supports title or date added

        self.form = BookSearch(self.request.GET)
        context_data['form'] = self.form
        # if form is valid, then search within the book and display matching pages
        # instead of volume info
        if self.form.is_valid():
            terms = self.form.search_terms()

            solr = solr_interface()
            query = solr.Q()
            for t in terms:
                # NOTE: should this be OR or AND?
                query |= solr.Q(page_text=t)
            # search for pages that belong to this book
            q = solr.query().filter(content_model=Page.PAGE_CMODEL_PATTERN,
                                    isConstituentOf=self.object.uri) \
                    .query(query) \
                    .field_limit(['page_order', 'pid'], score=True) \
                    .highlight('page_text', snippets=3) \
                    .sort_by('-score').sort_by('page_order') \
                    .results_as(SolrPage)

            # return highlighted snippets from page text
            # sort by relevance and then by page order

            # paginate the solr result set
            paginator = Paginator(q, 30)
            try:
                page = int(self.request.GET.get('page', '1'))
            except ValueError:
                page = 1
            try:
                results = paginator.page(page)
            except (EmptyPage, InvalidPage):
                results = paginator.page(paginator.num_pages)

            # NOTE: highlight snippets are available at
            # results.object_list.highlighting but are *NOT* currently
            # getting propagated to solrpage objects

            # url parameters for pagination
            url_params = self.request.GET.copy()
            if 'page' in url_params:
                del url_params['page']

            context_data.update({
                'pages': results,
                'url_params': urlencode(url_params),
                # provided for consistency with class-based view pagination
                'paginator': paginator,
                'page_obj': results,
            })

        else:
            # if not searching the volume, get annotation count for display
            # - annotation is only possibly on books with pages loaded
            if self.object.has_pages:
                # uses same dictionary lookup form as for browse/search volume
                annotation_count = self.object.annotation_count(self.request.user)
                if annotation_count != 0:
                    context_data['annotated_volumes'] = {
                        self.object.get_absolute_url(): annotation_count
                    }

        return context_data


class VolumePageList(ListView, VaryOnCookieMixin):

    template_name = 'books/volume_pages_list.html'
    paginate_by = 30
    context_object_name = 'pages'

    @method_decorator(last_modified(view_helpers.volume_pages_modified))
    def dispatch(self, *args, **kwargs):
        return super(VolumePageList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        self.repo = Repository(request=self.request)
        # store the volume for use in get_context_data
        self.vol = self.repo.get_object(self.kwargs['pid'], type=Volume)
        if not self.vol.exists or not self.vol.is_a_volume:
            raise Http404
        return self.vol.find_solr_pages()

    def get_context_data(self, **kwargs):
        context_data = super(VolumePageList, self).get_context_data()

        context_data.update({
            'vol': self.vol,
            'form': BookSearch(), # form for searching in this book
        })

        # if user is authenticated, check for annotations on this volume
        if self.request.user.is_authenticated():
            notes = self.vol.page_annotation_count(self.request.user)
            # method returns a dict for easy lookup;
            # strip out base site url for easy lookup in the template
            # (need leading / left to match item urls)
            domain = get_current_site(self.request).domain.rstrip('/')
            if not domain.startswith('http'):
                domain = 'http://' + domain
            annotated_pages = dict([(k.replace(domain, ''), v)
                                   for k, v in notes.iteritems()])
        else:
            annotated_pages = {}
        context_data['annotated_pages'] = annotated_pages

        # Check if the first page of the volume is wider than it is tall
        # to set the layout of the pages
        first_page = self.vol.pages[0]
        if first_page.width > first_page.height:
            layout = 'landscape'
        else:
            layout = 'default'
        context_data['layout'] = layout

        return context_data

#: size used for scaling single page image
SINGLE_PAGE_SIZE = 1000

class PageDetail(DetailView, VaryOnCookieMixin):
    '''View a single page in a book.'''
    model = Page
    template_name = 'books/page_detail.html'
    context_object_name = 'page'

    @method_decorator(last_modified(view_helpers.page_modified))
    def dispatch(self, *args, **kwargs):
        return super(PageDetail, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        # NOTE: type inferring repository needed to load pages as correct type
        # of Page (v1.0 or v1.1)
        repo = TypeInferringRepository(request=self.request)
        page = repo.get_object(self.kwargs['pid'])
        if not page.exists or not isinstance(page, Page):
            raise Http404
        return page

    def get_context_data(self, **kwargs):
        context_data = super(PageDetail, self).get_context_data()
        # use solr to find adjacent pages to this one
        pagequery = self.object.volume.find_solr_pages()
        # search range around current page order
        # (+/-1 should probably work, but using 2 to allow some margin for error)
        pagequery = pagequery.query(page_order__range=(self.object.page_order - 2,
                                                       self.object.page_order + 2))

        # find the index of the current page in the sorted solr result
        index = 0
        prev = nxt = None
        for p in pagequery:
            if p['pid'] == self.object.pid:
                break
            index += 1
            prev = p

        if len(pagequery) > index + 1:
            nxt = pagequery[index + 1]

        # calculates which paginated page the page is part of based on 30 items per page
        page_chunk = ((self.object.page_order - 1) // 30) + 1

        # form for searching in this book
        form = BookSearch()

        # currently only pagev1_1 has tei
        if hasattr(self.object, 'tei') and self.object.tei.exists:
            # determine scale for positioning OCR text in TEI facsimile
            # based on original image size in the OCR and image as displayed
            # - find maximum of width/height
            long_edge  = max(self.object.tei.content.page.width,
                self.object.tei.content.page.height)
            # NOTE: using the size from image the OCR was run on, since that
            # may or may not match the size of the master image loaded in
            # fedora, but the aspect ration should be kept the same from
            # original -> repository copy -> scaled copy used for display

            # - determine scale to convert original size to display size
            scale = float(SINGLE_PAGE_SIZE) / float(long_edge)
            logger.debug('page size is %s, long edge is %s, scale is %f' % \
                (SINGLE_PAGE_SIZE, long_edge, scale))
        else:
            scale = None

        context_data.update({'next': nxt, 'prev': prev,
            'page_chunk': page_chunk, 'form': form, 'scale': scale})
        return context_data

class PageDatastreamView(RawDatastreamView):
    '''Base view for :class:`~readux.books.models.Page` datastreams.'''
    object_type = Page
    datastream_id = None
    accept_range_request = False
    pid_url_kwarg = 'pid'
    repository_class = Repository


class PageOcr(PageDatastreamView):
    '''Display the page-level OCR content, if available (for
    :class:`~readux.books.models.PageV1_1` objects this is xml,
    for :class:`~readux.books.models.PageV1_0` this is text).  Returns a
    404 if this page object does not have page-level OCR.'''
    object_type = PageV1_1
    datastream_id = PageV1_1.ocr.id


class PageTei(PageDatastreamView):
    '''Display the page-level TEI facsimile, if available.  404 if this page
    object does not have TEI facsimile.'''
    datastream_id = Page.tei.id

    def get_headers(self):
        return {
            # generate a default filename based on the object pid
            'Content-Disposition': 'filename="%s_tei.xml"' % \
                 self.kwargs['pid'].replace(':', '-')
        }

class VolumeDatastreamView(RawDatastreamView):
    '''Base view for :class:`~readux.books.models.Volume` datastreams.'''
    object_type = Volume
    datastream_id = None
    accept_range_request = False
    pid_url_kwarg = 'pid'
    repository_class = Repository


class VolumePdf(VolumeDatastreamView):
    '''View to allow access to the PDF datastream of a
    :class:`~readux.books.models.Volume` object.  Sets a
    content-disposition header that will prompt the file to be saved
    with a default title based on the object label.  If **download** is specified
    in the query string (i.e., url/to/pdf/?download), then content-disposition
    will be set to attachment, prompting for download.'''
    datastream_id = Volume.pdf.id

    def get_headers(self):
        download = 'download' in self.request.GET
        # if download is requested, set content-disposition to prompt download
        attachment = 'attachment; ' if download else ''
        # retrieve the object so we can use it to set the download filename
        obj = self.get_repository().get_object(self.kwargs['pid'], type=self.object_type)
        if not obj.exists:
            raise Http404

        if obj.exists:  # assuming if exists passes we can get a label
            return {
                # generate a default filename based on the object label
                'Content-Disposition': '%sfilename="%s.pdf"' % \
                    (attachment, obj.label.replace(' ', '-'))
                }


class VolumeOcr(VolumeDatastreamView):
    '''View to allow access the raw OCR xml datastream of a
    :class:`~readux.books.models.Volume` object.
    '''
    datastream_id = VolumeV1_0.ocr.id


class VolumeText(VolumeOcr):
    '''View to allow access the plain text content of a
    :class:`~readux.books.models.Volume` object.
    '''
    # inherit to get etag/last-modified for ocr datastream

    # NOTE:  type-inferring is required here because volume could be either
    # v1.0 or v.1.1 and method to pull the text content is different
    repository_class = TypeInferringRepository

    def get(self, request, *args, **kwargs):
        repo = self.get_repository()
        obj = repo.get_object(self.kwargs['pid'])
        # if object doesn't exist, isn't a volume, or doesn't have ocr text - 404
        if not obj.exists or not obj.has_requisite_content_models or not obj.fulltext_available:
            raise Http404

        response = HttpResponse(obj.get_fulltext(), 'text/plain')
        # generate a default filename based on the object label
        response['Content-Disposition'] = 'filename="%s.txt"' % \
            obj.label.replace(' ', '-')

        # NOTE: currently etag/last-modified will only work
        # for volume v1.0 objects with an ocr datastream
        return response

class VolumeTei(View):

    def get(self, request, *args, **kwargs):
        repo = TypeInferringRepository()
        vol = repo.get_object(self.kwargs['pid'])
        # if object doesn't exist, isn't a volume, or doesn't have tei text - 404
        if not vol.exists or not vol.has_requisite_content_models or not vol.has_tei:
            raise Http404

        tei = vol.generate_volume_tei()
        base_filename = '%s-tei' % vol.noid
        if kwargs.get('mode', None) == 'annotated':
            tei = annotate.annotated_tei(tei, vol.annotations(user=request.user))
            base_filename += '-annotated'

        response = HttpResponse(tei.serialize(pretty=True),
            content_type='application/xml')
        # generate a default filename based on the object label
        response['Content-Disposition'] = 'attachment;filename="%s.xml"' % \
            base_filename
        response.set_cookie('%s-tei-export' % vol.noid, 'complete', max_age=10)
        return response


class AnnotatedVolumeExport(View):
    export_modes = ['static', 'jekyll']

    def get(self, request, *args, **kwargs):
        repo = TypeInferringRepository()
        vol = repo.get_object(self.kwargs['pid'])
        # if object doesn't exist, isn't a volume, or doesn't have tei text - 404
        if not vol.exists or not vol.has_requisite_content_models or not vol.has_tei:
            raise Http404

        # currently, supported modes are static (built) site and jekyll
        mode = kwargs.get('mode', 'static')
        if mode not in self.export_modes:
            return HttpResponseBadRequest('Export mode "%s" is not supported' % mode)

        static_site = mode == 'static'

        # generate annotated tei
        tei = annotate.annotated_tei(vol.generate_volume_tei(),
            vol.annotations(user=request.user))
        webzipfile = export.website(vol, tei, static=static_site)
        response = StreamingHttpResponse(FileWrapper(webzipfile, 8192),
                content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="%s_annotated_%s_site.zip"' % \
            (vol.noid, mode)
        response['Content-Length'] = os.path.getsize(webzipfile.name)
        # set a cookie to indicate download is complete; used by javascript
        # to hide waiting indicator
        # TODO: html request should probably be a post, and include cookie name
        response.set_cookie('%s-%s-export' % (vol.noid, mode),
            'complete', max_age=10)
        return response


class Unapi(View):
    '''unAPI service point for :class:`~readux.books.models.Volume` objects,
    to make content available for harvest via Zotero.'''

    # NOTE: this could probably be generalized into a re-usable view

    @method_decorator(condition(etag_func=view_helpers.unapi_etag,
        last_modified_func=view_helpers.unapi_modified))
    def dispatch(self, *args, **kwargs):
        return super(Unapi, self).dispatch(*args, **kwargs)

    def get(self, request):
        context = {}
        item_id = request.GET.get('id', None)
        fmt = request.GET.get('format', None)
        if item_id is not None:
            context['id'] = item_id
            repo = Repository(request=self.request)
            # generalized class-based view would need probably a get-item method
            # for repo objects, could use type-inferring repo variant
            obj = repo.get_object(item_id, type=Volume)

            formats = obj.unapi_formats

            if fmt is None:
                # display formats for this item
                context['formats'] = formats
            else:
                current_format = formats[fmt]
                # return requested format for this item
                meth = getattr(obj, current_format['method'])
                return HttpResponse(meth(), content_type=current_format['type'])

        else:
            # display formats for all items
            # NOTE: if multiple classes, should be able to combine the formats
            context['formats'] = Volume.unapi_formats

        # NOTE: doesn't really even need to be a template, could be generated
        # with eulxml just as easily if that simplifies reuse
        return render(request, 'books/unapi_format.xml', context,
            content_type='application/xml')



def _error_image_response(mode):
    # error image http response for 401/404/500 errors when serving out
    # images from fedora
    error_images = {
        'thumbnail': 'notfound_thumbnail.png',
        'single-page': 'notfound_page.png',
        'mini-thumbnail': 'notfound_mini_thumbnail_page.png',
    }
    # need a different way to catch it
    if mode in error_images:
        img = error_images[mode]

        if settings.DEBUG:
            base_path = settings.STATICFILES_DIRS[0]
        else:
            base_path = settings.STATIC_ROOT
        with open(os.path.join(base_path, 'img', img)) as content:
            return HttpResponseNotFound(content.read(), content_type='image/png')


class PageRedirect(RedirectView):
    # redirect view for old page urls without volume pids
    pattern_name = 'books:page'
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        # NOTE: type inferring repository needed to load pages as correct type
        # of Page (v1.0 or v1.1)
        repo = TypeInferringRepository()
        page = repo.get_object(kwargs['pid'])
        if not page.exists or not isinstance(page, Page):
            raise Http404
        page_url = reverse(self.pattern_name,
            kwargs={'vol_pid': page.volume.pid, 'pid': page.pid})
        return ''.join([page_url, kwargs['path']])


class ProxyView(View):
    # quick and dirty proxyview modeled on RedirectView

    def get(self, request, *args, **kwargs):
        url = self.get_redirect_url(*args, **kwargs)
        # use headers to allow browsers to cache downloaded copies
        headers = {}
        for header in ['HTTP_IF_MODIFIED_SINCE', 'HTTP_IF_UNMODIFIED_SINCE',
                       'HTTP_IF_MATCH', 'HTTP_IF_NONE_MATCH']:
            if header in request.META:
                headers[header.replace('HTTP_', '')] = request.META.get(header)
        remote_response = requests.get(url, headers=headers)
        local_response = HttpResponse()
        local_response.status_code = remote_response.status_code

        # include response headers, except for server-specific items
        for header, value in remote_response.headers.iteritems():
            if header not in ['Connection', 'Server', 'Keep-Alive', 'Link']:
                             # 'Access-Control-Allow-Origin', 'Link']:
                # FIXME: link header is valuable, but would
                # need to be made relative to current url
                local_response[header] = value

        # special case, for deep zoom (hack)
        if kwargs['mode'] == 'info':
            data = remote_response.json()
            # need to adjust the id to be relative to current url
            # this is a hack, patching in a proxy iiif interface at this url
            data['@id'] = absolutize_url(request.path.replace('/info/', '/iiif'))
            local_response.content = json.dumps(data)
            # upate content-length for change in data
            local_response['content-length'] = len(local_response.content)
        else:
            # include response content if any
            local_response.content = remote_response.content

        return local_response

    def head(self, request, *args, **kwargs):
        url = self.get_redirect_url(*args, **kwargs)
        remote_response = requests.head(url)
        response = HttpResponse()
        for header, value in remote_response.headers.iteritems():
            if header not in ['Connection', 'Server', 'Keep-Alive',
                             'Access-Control-Allow-Origin', 'Link']:
                response[header] = value
        return response


# class PageImage(RedirectView):
# NOTE: previously, was redirecting to loris, but currently the loris
# image server is not externally accessible

class PageImage(ProxyView):
    '''Local view for page images.  These all return redirects to the
    configured IIIF image viewer, but allow for a local, semantic
    image url independent of image handling implementations
    to be referenced in annotations and exports.'''

    def get_redirect_url(self, *args, **kwargs):
        repo = TypeInferringRepository()
        page = repo.get_object(kwargs['pid'], type=Page)

        if kwargs['mode'] == 'thumbnail':
            return page.iiif.thumbnail()
        elif kwargs['mode'] == 'mini-thumbnail':
            return page.iiif.mini_thumbnail()
        elif kwargs['mode'] == 'single-page':
            return page.iiif.page_size()
        elif kwargs['mode'] == 'fs':  # full size
            return page.iiif
        elif kwargs['mode'] == 'info':
            # TODO: needs an 'Access-Control-Allow-Origin' header
            # to allow jekyll sites to use for deep zoom
            return page.iiif.info()
        elif kwargs['mode'] == 'iiif':
            return page.iiif.info().replace('info.json', kwargs['url'].rstrip('/'))
