from django import forms
from django.contrib.admin.widgets import SELECT2_TRANSLATIONS
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.urls import path
from django.utils.translation import get_language


class AutocompleteFilterMixin:
    @property
    def media(self):
        media = super().media

        i18n_file = None
        i18n_name = SELECT2_TRANSLATIONS.get(get_language(), None)
        if i18n_name:
            i18n_file = "admin/js/vendor/select2/i18n/%s.js" % i18n_name

        extra_js = [
            "admin/js/vendor/jquery/jquery.js",
            "admin/js/vendor/select2/select2.full.js",
        ]
        if i18n_file:
            extra_js.append(i18n_file)
        extra_js.extend(
            [
                "admin/js/jquery.init.js",
                "admin/js/autocomplete.js",
                "admin/js/autocomplete_filter.js",
            ]
        )
        extra_css = [
            "admin/css/vendor/select2/select2.css",
            "admin/css/autocomplete.css",
        ]
        return media + forms.Media(js=extra_js, css={"screen": extra_css})

    def get_urls(self):
        """The searches of the list's AutocompleteFilters."""
        opts = self.model._meta
        name = "%s_%s_autocomplete_filter" % (opts.app_label, opts.model_name)
        view = self.admin_site.admin_view(self.autocomplete_filter_view)
        return [
            path("autocomplete-filter/<str:parameter>/", view, name=name),
            *super().get_urls(),
        ]

    def autocomplete_filter_view(self, request, parameter):
        """One page of an AutocompleteFilter's search, as the admin's select2 widget reads it."""
        from .filters import AutocompleteFilter

        if not self.has_view_permission(request):
            raise PermissionDenied
        for list_filter in self.get_list_filter(request):
            if (
                isinstance(list_filter, type)
                and issubclass(list_filter, AutocompleteFilter)
                and list_filter.parameter_name == parameter
            ):
                break
        else:
            raise Http404("No such filter.")
        found = list_filter(request, {}, self.model, self)
        try:
            page = max(int(request.GET.get("page", 1)), 1)
        except ValueError:
            page = 1
        size = found.page_size
        start = (page - 1) * size
        results = list(
            found.search(request, request.GET.get("term", "").strip())[
                start : start + size + 1
            ]
        )
        return JsonResponse(
            {
                "results": [
                    {"id": str(value), "text": str(label)}
                    for value, label in results[:size]
                ],
                "pagination": {"more": len(results) > size},
            }
        )
