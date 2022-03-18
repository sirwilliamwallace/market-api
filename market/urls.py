from django.urls import path

from . import views

urlpatterns = [
    # products urls
    path('product/insert/', views.product_insert, name='product_insert'),
    path('product/list/', views.product_list, name='product_list'),
    # TODO: insert other url paths
]
