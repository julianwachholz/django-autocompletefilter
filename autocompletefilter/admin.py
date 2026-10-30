from django import forms
from django.contrib.admin.widgets import SELECT2_TRANSLATIONS
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
