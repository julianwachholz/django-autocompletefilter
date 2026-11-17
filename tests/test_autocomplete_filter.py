"""AutocompleteFilter and the view AutocompleteFilterMixin serves its searches from."""
import pytest
from django.contrib import admin
from django.test import RequestFactory

from autocompletefilter.filters import AutocompleteFilter

from .conftest import filter_selects, query, titles
from .testapp.models import Book

URL = "/admin/testapp/book/"
SEARCH_URL = "/admin/testapp/book/autocomplete-filter/genre/"


def genre_select(response):
    return filter_selects(response)["genre"]


def test_search(admin_client, library):
    response = admin_client.get(SEARCH_URL, {"term": "  fan "})
    assert response.status_code == 200
    assert response.json() == {
        "results": [{"id": "fantasy", "text": "FANTASY"}],
        "pagination": {"more": False},
    }


def test_search_is_paginated(admin_client, library):
    Book.objects.create(title="Gone Girl", genre="thriller")  # page_size is 2

    first = admin_client.get(SEARCH_URL).json()
    assert [result["id"] for result in first["results"]] == ["fantasy", "scifi"]
    assert first["pagination"] == {"more": True}

    second = admin_client.get(SEARCH_URL, {"page": 2}).json()
    assert [result["id"] for result in second["results"]] == ["thriller"]
    assert second["pagination"] == {"more": False}


@pytest.mark.parametrize("page", ["x", "0", "-3"])
def test_search_with_a_bad_page_is_the_first_page(admin_client, library, page):
    assert admin_client.get(SEARCH_URL, {"page": page}).json() == (
        admin_client.get(SEARCH_URL).json()
    )


def test_search_of_an_unknown_filter(admin_client, library):
    response = admin_client.get("/admin/testapp/book/autocomplete-filter/nope/")
    assert response.status_code == 404


def test_search_needs_a_login(client, library):
    response = client.get(SEARCH_URL)
    assert response.status_code == 302
    assert response["Location"].startswith("/admin/login/")


def test_search_needs_the_view_permission(client, library, django_user_model):
    user = django_user_model.objects.create_user("staff", is_staff=True)
    client.force_login(user)
    assert client.get(SEARCH_URL).status_code == 403


def test_renders_the_autocomplete_widget(admin_client, library):
    select = genre_select(admin_client.get(URL))
    attrs = select["attrs"]
    assert attrs["data-ajax--url"] == SEARCH_URL
    assert attrs["data-field-name"] == "genre"
    assert "admin-autocomplete" in attrs["class"].split()
    assert select["options"] == []


def test_filters_and_shows_the_selected_value(admin_client, library):
    response = admin_client.get(URL, {"genre": "fantasy"})
    assert titles(response) == ["The Hobbit", "The Silmarillion"]
    assert genre_select(response)["options"] == [
        {"value": "fantasy", "text": "FANTASY"}
    ]


def test_query_strings(admin_client, library):
    response = admin_client.get(URL, {"genre": "fantasy", "q": "the"})
    attrs = genre_select(response)["attrs"]
    placeholder = attrs["data-querystring-placeholder"]
    assert query(attrs["data-querystring"]) == {"genre": [placeholder], "q": ["the"]}
    assert query(attrs["data-querystring-all"]) == {"q": ["the"]}


def test_url_of_a_custom_admin_site(admin_client, library):
    response = admin_client.get("/custom/testapp/book/")
    url = genre_select(response)["attrs"]["data-ajax--url"]
    assert url == "/custom/testapp/book/autocomplete-filter/genre/"
    assert admin_client.get(url, {"term": "sci"}).json()["results"] == [
        {"id": "scifi", "text": "SCIFI"}
    ]


def test_search_must_be_implemented():
    class Unsearchable(AutocompleteFilter):
        title = "unsearchable"
        parameter_name = "unsearchable"

    request = RequestFactory().get("/")
    list_filter = Unsearchable(request, {}, Book, admin.site._registry[Book])
    with pytest.raises(NotImplementedError):
        list_filter.search(request, "")
