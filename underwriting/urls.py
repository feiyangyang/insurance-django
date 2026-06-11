from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("customer/", views.customer_list, name="customer_list"),
    path("customer/add/", views.customer_add, name="customer_add"),
    path("customer/<int:customer_id>/edit/", views.customer_edit, name="customer_edit"),
    path("customer/<int:customer_id>/delete/", views.customer_delete, name="customer_delete"),
]