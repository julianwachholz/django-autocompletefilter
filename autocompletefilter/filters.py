from django.contrib.admin.filters import RelatedFieldListFilter
from django.urls import NoReverseMatch, reverse


def get_request():
    """Walk the stack up to find a request in a context variable."""
    import inspect
    frame = None
    try:
        for f in inspect.stack()[1:]:
            frame = f[0]
            code = frame.f_code
            if code.co_varnames and 'context' in code.co_varnames:
                return frame.f_locals['context']['request']
    finally:
        del frame


class AutocompleteListFilter(RelatedFieldListFilter):
    """Admin list_filter using autocomplete select 2 widget."""

    template = 'admin/filter_autocomplete.html'

    def has_output(self):
        """Show the autocomplete filter at all times."""
        return True

    @staticmethod
    def get_admin_namespace():
        request = get_request()
        return request.resolver_match.namespace

    def get_url(self):
        model = self.field.related_model
        args = (
            model._meta.app_label,
            model._meta.model_name,
        )
        try:
            return reverse('admin:%s_%s_autocomplete' % args)
        except NoReverseMatch:
            # Admin is registered under a different namespace!
            args = (
                self.get_admin_namespace(),
                *args,
            )
            return reverse('%s:%s_%s_autocomplete' % args)

    def field_choices(self, field, request, model_admin):
        # Do not populate the field choices with a huge queryset
        return []

    def choices(self, changelist):
        """
        Get choices for the widget.

        Yields a single choice populated with template context variables.

        """
        url = self.get_url()

        placeholder = 'PKVAL'
        query_string = changelist.get_query_string({
            self.lookup_kwarg: placeholder,
        }, [self.lookup_kwarg_isnull])

        lookup_display = None
        if self.lookup_val:
            instance = self.field.related_model.objects.get(pk=self.lookup_val)
            lookup_display = str(instance)

        yield {
            'url': url,
            'selected': self.lookup_val,
            'selected_display': lookup_display,
            'query_string': query_string,
            'query_string_placeholder': placeholder,
            'query_string_all': changelist.get_query_string(
                {}, [self.lookup_kwarg, self.lookup_kwarg_isnull]
            ),
        }
