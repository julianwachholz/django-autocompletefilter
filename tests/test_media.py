"""The scripts and styles AutocompleteFilterMixin adds to the model admin."""
import re

from django.contrib import admin
from django.utils import translation

from .testapp.models import Book


def media(language):
    with translation.override(language):
        return admin.site._registry[Book].media


def scripts(language):
    """The script paths as rendered, without the STATIC_URL."""
    return re.findall(r'src="/static/([^"]+)"', "".join(media(language).render_js()))


def test_scripts_are_in_loading_order():
    js = scripts("en")
    order = [
        "admin/js/vendor/jquery/jquery.js",
        "admin/js/vendor/select2/select2.full.js",
        "admin/js/vendor/select2/i18n/en.js",
        "admin/js/jquery.init.js",
        "admin/js/autocomplete.js",
        "admin/js/autocomplete_filter.js",
    ]
    assert [path for path in js if path in order] == order


def test_styles():
    css = media("en")._css["screen"]
    assert "admin/css/vendor/select2/select2.css" in css
    assert "admin/css/autocomplete.css" in css


def test_select2_translation_of_the_language():
    assert "admin/js/vendor/select2/i18n/de.js" in scripts("de")


def test_no_select2_translation_of_an_unsupported_language():
    assert not [path for path in scripts("xx") if "/i18n/" in path]
