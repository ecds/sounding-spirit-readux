from django.template import Library

register = Library()


@register.filter_function
def order_by(queryset, args):
    args = [x.strip() for x in args.split(",")]
    return queryset.order_by(*args)


@register.filter
def dict_item(dictionary, key):
    """'Template filter to allow accessing dictionary value by variable key.
    Example use::

        {{ mydict|dict_item:keyvar }}
    """
    # adapted from Princeton-CDH/geniza project https://github.com/Princeton-CDH/geniza/
    try:
        return dictionary[key]
    except AttributeError:
        # fail silently if something other than a dict is passed
        return None
