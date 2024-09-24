import pytest
from django.contrib.admin.sites import site

from test_project.test_app.models import RelatedModel
from test_project.test_app.admin import RelatedModelAdmin


@pytest.mark.django_db
def test_modeladmin_has_js_file(admin_client):
    # Given a ModelAdmin with the AutocompleteFilterMixin
    model_admin = site._registry[RelatedModel]
    assert isinstance(model_admin, RelatedModelAdmin)

    css_file = "admin/css/vendor/select2/select2.css"
    js_file = "admin/js/vendor/jquery/jquery.js"

    media = model_admin.media

    # Then the ModelAdmin's media should include the expected CSS and JS files
    assert (
        css_file in media._css["screen"]
    ), f"{css_file} is not included in the ModelAdmin's media"
    assert js_file in media._js, f"{js_file} is not included in the ModelAdmin's media"
