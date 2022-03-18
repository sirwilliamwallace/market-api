from django.urls import path

from . import views

urlpatterns = [
    # products urls
    path('product/insert/', views.product_insert, name='product_insert'),
    path('product/list/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    # TODO: insert other url paths
]
