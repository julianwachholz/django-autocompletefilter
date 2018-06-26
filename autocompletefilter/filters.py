from django.contrib.admin.filters import RelatedFieldListFilter
from django.urls import reverse


class AutocompleteListFilter(RelatedFieldListFilter):
    """Admin list_filter using autocomplete select 2 widget."""

    template = 'admin/filter_autocomplete.html'

    def has_output(self):
        """Always show the autocomplete filter."""
        return True

    def get_url(self):
        model = self.field.related_model
        return reverse('admin:%s_%s_autocomplete' % (
            # self.admin_site.name,  # TODO get access to admin_site?
            model._meta.app_label,
            model._meta.model_name
        ))

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
