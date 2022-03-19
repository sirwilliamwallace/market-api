from django.urls import path
from . import views

urlpatterns = [
    path('customer/register/', views.register_customer, name='index'),
    path('customer/list/', views.list_customers, name='list_customers'),
    path('customer/login/', views.login_customer, name='login_customer'),
    path('customer/logout/', views.logout_customer, name='logout_customer'),
    path('customer/<int:customer_id>/', views.customer_detail, name='list_customers'),
    path('customer/<int:customer_id>/edit/', views.customer_edit, name='edit_customers'),
    path('customer/profile/', views.customer_profile, name='customer_profile'),
]
