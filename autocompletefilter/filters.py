import django
from django.contrib.admin.filters import RelatedFieldListFilter, SimpleListFilter
from django.urls import NoReverseMatch, reverse


def get_request():
    """Walk the stack up to find a request in a context variable."""
    import inspect

    frame = None
    try:
        for f in inspect.stack()[1:]:
            frame = f[0]
            code = frame.f_code
            if code.co_varnames and "context" in code.co_varnames:
                return frame.f_locals["context"]["request"]
    finally:
        del frame


class AutocompleteListFilter(RelatedFieldListFilter):
    """Admin list_filter using autocomplete select 2 widget."""

    template = "admin/filter_autocomplete.html"

    def has_output(self):
        """Show the autocomplete filter at all times."""
        return True

    @staticmethod
    def get_admin_namespace():
        request = get_request()
        return request.resolver_match.namespace

    def get_url(self):
        try:
            return reverse("admin:autocomplete")
        except NoReverseMatch:
            pass

        namespace = self.get_admin_namespace()
        return reverse("%s:autocomplete" % namespace)

    def field_choices(self, field, request, model_admin):
        # Do not populate the field choices with a huge queryset
        return []

    def choices(self, changelist):
        """
        Get choices for the widget.

        Yields a single choice populated with template context variables.

        """
        url = self.get_url()

        placeholder = "PKVAL"
        query_string = changelist.get_query_string(
            {self.lookup_kwarg: placeholder}, [self.lookup_kwarg_isnull]
        )

        selected = lookup_display = None
        if self.lookup_val:
            # Django 5.0 and later keep every value of the parameter, in a list
            if django.VERSION >= (5, 0):
                selected = self.lookup_val[-1]
            else:
                selected = self.lookup_val
            # an object deleted since the link was made selects nothing
            instance = self.field.related_model.objects.filter(pk=selected).first()
            if instance is None:
                selected = None
            else:
                lookup_display = str(instance)

        model = self.field.model

        yield {
            "url": url,
            "selected": selected,
            "selected_display": lookup_display,
            "query_string": query_string,
            "query_string_placeholder": placeholder,
            "query_string_all": changelist.get_query_string(
                {}, [self.lookup_kwarg, self.lookup_kwarg_isnull]
            ),
            # Data attrs for the generic autocomplete view
            "app_label": model._meta.app_label,
            "model_name": model._meta.model_name,
            "field_name": self.field.name,
        }


class AutocompleteFilter(SimpleListFilter):
    """
    A list filter for any value, not just a foreign key, with the same autocomplete widget.

    Instead of ``lookups()``, which lists every choice up front, a subclass implements
    ``search(request, term)``: the ``(value, label)`` pairs that match what was typed, as a
    list or a queryset of pairs (sliced into pages of ``page_size``). ``queryset()`` filters
    by ``self.value()`` as usual, and ``label(request, value)`` names the chosen value.
    The model admin needs ``AutocompleteFilterMixin``, which serves the searches.
    """

    template = "admin/filter_autocomplete.html"
    page_size = 20

    def __init__(self, request, params, model, model_admin):
        self.request = request  # for label()
        self.model_admin = model_admin  # for search(): model_admin.get_queryset(request) …
        super().__init__(request, params, model, model_admin)

    def lookups(self, request, model_admin):
        return []  # never every choice: search() finds them

    def has_output(self):
        return True

    def search(self, request, term):
        raise NotImplementedError(
            "subclasses of AutocompleteFilter must provide a search() method"
        )

    def label(self, request, value):
        return value

    def choices(self, changelist):
        opts = changelist.model._meta
        url = reverse(
            "%s:%s_%s_autocomplete_filter"
            % (changelist.model_admin.admin_site.name, opts.app_label, opts.model_name),
            args=[self.parameter_name],
        )
        placeholder = "PKVAL"
        value = self.value()
        yield {
            "url": url,
            "selected": value,
            "selected_display": self.label(self.request, value)
            if value
            else None,
            "query_string": changelist.get_query_string(
                {self.parameter_name: placeholder}
            ),
            "query_string_placeholder": placeholder,
            "query_string_all": changelist.get_query_string(
                remove=[self.parameter_name]
            ),
            "app_label": opts.app_label,
            "model_name": opts.model_name,
            "field_name": self.parameter_name,
        }
