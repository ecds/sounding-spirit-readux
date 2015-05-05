from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.generic import View
from eulcommon.djangoextras.http.responses import HttpResponseSeeOtherRedirect

from readux.annotations.models import Annotation

def root(request):
    # NOTE: would be convenient to include api links
    # similar to the reference implementation
    return JsonResponse({
      "name": "Annotator Store API",
      "version": "2.0.0"  # ??
    })


non_ajax_error_msg = 'Currently Annotations can only be updated or created via AJAX.'

class Annotations(View):
    '''api/annotations

    On GET, lists annotations.
    On AJAX POST with json data in request body, creates a new
    annotation.'''

    def get(self, request):
        # TODO: pagination; look at reference implementation
        notes = Annotation.objects.all()
        # TODO: filter by permissions
        return JsonResponse([n.info() for n in notes], safe=False)

    def post(self, request):
        # for now, only support creation via ajax
        if request.is_ajax():
            note = Annotation.create_from_request(request)
            note.save()
            # annotator store documentation says to return 303
            # not sure why this isn't a 201 Created...
            return HttpResponseSeeOtherRedirect(note.get_absolute_url())

        else:
            return HttpResponseBadRequest(non_ajax_error_msg)


class AnnotationView(View):
    '''Views for displaying, updating, and removing a single Annotation.'''
    # TODO: check permissions for get/put/delete

    def get_object(self):
        print 'get object'
        print 'self.kwargs = ', self.kwargs

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        slug = self.kwargs.get(self.slug_url_kwarg, None)


    def get_annotation(self, id):
        # common functionality for all views
        return get_object_or_404(Annotation, id=id)

    def get(self, request, id):
        '''Display the JSON information for the requested annotation.'''
        # NOTE: if id is not a valid uuid this results in a ValueError
        # instead of a 404; should be handled by uuid regex in url config
        note = self.get_annotation(id)
        return JsonResponse(note.info())

    def put(self, request, id):
        '''Update the annotation via JSON data posted by AJAX.'''
        if request.is_ajax():
            note = self.get_annotation(id)
            note.update_from_request(request)
            return HttpResponseSeeOtherRedirect(note.get_absolute_url())
        else:
            return HttpResponseBadRequest(non_ajax_error_msg)

    # on DELETE, remove
    def delete(self, request, id):
        '''Remove the annotation.
        Returns a 204 No Content as per Annotator store API documentation.'''
        note = self.get_annotation(id)
        note.delete()
        response = HttpResponse('')
        # return 204 no content, according to annotator store api docs
        response.status_code = 204
        return response


def search(request):
    # TODO: what other search fields should be supported?
    # also TODO: limit/offset options for pagination
    uri = request.GET.get('uri', None)
    text = request.GET.get('text', None)
    user = request.GET.get('user', None)
    notes = Annotation.objects.all()
    if uri is not None:
        notes = notes.filter(uri=uri)
    if text is not None:
        notes = notes.filter(text__icontains=text)
    if user is not None:
        notes = notes.filter(user__username=user)
    return JsonResponse({
        'total': notes.count(),
        'rows': [n.info() for n in notes]
    })