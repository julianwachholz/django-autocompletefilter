"""AutocompleteListFilter: the filter on a foreign key."""
import pytest

from .conftest import filter_selects, query, titles
from .testapp.models import Author

URL = "/admin/testapp/book/"


def author_select(response):
    return filter_selects(response)["author"]


def test_renders_the_autocomplete_widget(admin_client, library):
    select = author_select(admin_client.get(URL))
    attrs = select["attrs"]
    assert attrs["data-ajax--url"] == "/admin/autocomplete/"
    assert attrs["data-app-label"] == "testapp"
    assert attrs["data-model-name"] == "book"
    assert attrs["data-field-name"] == "author"
    assert "admin-autocomplete" in attrs["class"].split()


def test_never_lists_the_related_objects(admin_client, library):
    assert author_select(admin_client.get(URL))["options"] == []


@pytest.mark.parametrize("authors", [0, 1])
def test_is_shown_with_too_few_objects_to_filter_by(admin_client, db, authors):
    # a RelatedFieldListFilter hides itself with fewer than two choices
    for n in range(authors):
        Author.objects.create(name="Author %d" % n)
    assert "author" in filter_selects(admin_client.get(URL))


def test_filters_and_shows_the_selected_object(admin_client, library):
    tolkien = library["tolkien"]
    response = admin_client.get(URL, {"author__id__exact": tolkien.pk})
    assert titles(response) == ["The Hobbit", "The Silmarillion"]
    assert author_select(response)["options"] == [
        {"value": str(tolkien.pk), "text": "Tolkien"}
    ]


def test_a_deleted_object_selects_nothing(admin_client, library):
    response = admin_client.get(URL, {"author__id__exact": 12345})
    assert titles(response) == []
    assert author_select(response)["options"] == []


def test_query_strings(admin_client, library):
    response = admin_client.get(
        URL, {"author__id__exact": library["tolkien"].pk, "q": "the"}
    )
    attrs = author_select(response)["attrs"]
    placeholder = attrs["data-querystring-placeholder"]
    assert query(attrs["data-querystring"]) == {
        "author__id__exact": [placeholder],
        "q": ["the"],
    }
    assert query(attrs["data-querystring-all"]) == {"q": ["the"]}


def test_the_admin_autocomplete_view_accepts_the_widget(admin_client, library):
    attrs = author_select(admin_client.get(URL))["attrs"]
    response = admin_client.get(
        attrs["data-ajax--url"],
        {
            "term": "tol",
            "app_label": attrs["data-app-label"],
            "model_name": attrs["data-model-name"],
            "field_name": attrs["data-field-name"],
        },
    )
    assert response.status_code == 200
    assert response.json()["results"] == [
        {"id": str(library["tolkien"].pk), "text": "Tolkien"}
    ]


@pytest.mark.urls("tests.urls_custom")
def test_url_of_a_custom_admin_site(admin_client, library):
    response = admin_client.get("/custom/testapp/book/")
    assert author_select(response)["attrs"]["data-ajax--url"] == "/custom/autocomplete/"
