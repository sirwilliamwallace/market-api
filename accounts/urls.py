from django.urls import path
from . import views


urlpatterns = [
    path('customer/register/', views.register_customer, name='index'),
    path('customer/list/', views.list_customers , name='list_users'),
    path('customer/<int:customer_id>/', views.customer_detail , name='list_users'),
    path('customer/<int:customer_id>/edit/', views.customer_edit , name='edit_users'),
]

