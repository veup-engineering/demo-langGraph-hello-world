from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path("articles/", views.list_articles, name="list-articles"),
    path("articles/search/", views.search_articles, name="search-articles"),
    path("products/", views.list_products, name="list-products"),
    path("products/search/", views.search_products, name="search-products"),
]
