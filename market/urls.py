from django.urls import path

from . import views

urlpatterns = [
    # products urls
    path('product/insert/', views.product_insert, name='product_insert'),
    path('product/list/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/edit_inventory/', views.edit_inventory, name='edit_inventory'),
    # TODO: insert other url paths
    path('shopping/cart/', views.shopping_cart, name='shopping_cart'),
    path('shopping/cart/add_items/', views.add_to_cart, name='add_to_cart'),
    path('shopping/cart/remove_items/', views.remove_from_cart, name='remove_from_cart'),
    path('shopping/submit/', views.submit_cart, name='submit_cart'),
]
