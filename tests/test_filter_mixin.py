import django
import pytest
from django.contrib.admin.sites import site
from django.urls import reverse

from test_project.test_app.models import ExampleModel, RelatedModel
from test_project.test_app.admin import RelatedModelAdmin


@pytest.mark.django_db
def test_autocomplete_filter_renders_correct_html_without_selected_object(admin_client):
    # Given a ModelAdmin with the AutocompleteFilterMixin
    model_admin = site._registry[RelatedModel]
    assert isinstance(model_admin, RelatedModelAdmin)

    # When we request the changelist for the model
    url = reverse("admin:test_app_relatedmodel_changelist")
    response = admin_client.get(url)
    data = response.content.decode()

    assert response.status_code == 200

    expected_autocomplete_url = reverse(
        "admin:autocomplete"
        if django.VERSION > (3, 2)
        else "admin:test_app_examplemodel_autocomplete"
    )

    # Then the response should include the expected HTML for the filter
    assert (
        f"""<select id="filter_example model"
        data-ajax--cache
        data-ajax--type="GET"
        data-ajax--url="{expected_autocomplete_url}"
        data-theme="admin-autocomplete"
        data-allow-clear="true"
        data-placeholder="Example Model"
        data-querystring="?example_model__id__exact=PKVAL"
        data-querystring-placeholder="PKVAL"
        data-querystring-all="?"
        data-app-label="test_app"
        data-model-name="relatedmodel"
        data-field-name="example_model"
        style="width:210px;"
        class="admin-autocomplete admin-autocomplete-filter"
    >"""
        in data
    )


@pytest.fixture
def test_instance():
    test_instance_1 = ExampleModel.objects.create(
        id=10,
        name="Test Object 1",
    )
    test_instance_2 = ExampleModel.objects.create(
        id=11,
        name="Test Object 2",
    )
    RelatedModel.objects.create(
        id=998,
        name="Related 1",
        example_model=test_instance_1,
    )
    RelatedModel.objects.create(
        id=999,
        name="Related 2",
        example_model=test_instance_2,
    )
    return test_instance_1


@pytest.mark.skipif(
    django.VERSION >= (5,), reason="Filtering is currently broken in django 5+"
)
@pytest.mark.django_db
def test_autocomplete_filter_renders_correct_html_with_selected_object(admin_client, test_instance):
    # Given a ModelAdmin with the AutocompleteFilterMixin, and some related objects
    model_admin = site._registry[RelatedModel]
    assert isinstance(model_admin, RelatedModelAdmin)

    # When we request the changelist for the model with a filter applied
    url = reverse("admin:test_app_relatedmodel_changelist")
    filter_url = f"{url}?example_model__id__exact={test_instance.id}"
    response = admin_client.get(filter_url)

    assert response.status_code == 200

    data = response.content.decode()

    # Then the response should include the expected HTML for the filter
    expected_autocomplete_url = reverse(
        "admin:autocomplete"
        if django.VERSION > (3, 2)
        else "admin:test_app_examplemodel_autocomplete"
    )
    expected_option_html = (
        f"""<option selected value="[&#x27;{test_instance.id}&#x27;]">{test_instance.name}</option>"""
        if django.VERSION >= (5,)
        else f"""<option selected value="{test_instance.id}">{test_instance.name}</option>"""
    )

    expected_select_html = f"""<select id="filter_example model"
        data-ajax--cache
        data-ajax--type="GET"
        data-ajax--url="{expected_autocomplete_url}"
        data-theme="admin-autocomplete"
        data-allow-clear="true"
        data-placeholder="Example Model"
        data-querystring="?example_model__id__exact=PKVAL"
        data-querystring-placeholder="PKVAL"
        data-querystring-all="?"
        data-app-label="test_app"
        data-model-name="relatedmodel"
        data-field-name="example_model"
        style="width:210px;"
        class="admin-autocomplete admin-autocomplete-filter"
    >\n    \n        {expected_option_html}\n    \n    </select>"""

    assert expected_select_html in data

    # And the response should only include the related object that matches the filter
    assert (
        '<a href="/admin/test_app/relatedmodel/998/change/?_changelist_filters=example_model__id__exact%3D10">'
        "Related 1</a>" in data
    )
    # But doesn't include the other object
    assert (
        '<a href="/admin/test_app/relatedmodel/999/change/?_changelist_filters=example_model__id__exact%3D10">'
        "Related 2</a>" not in data
    )
