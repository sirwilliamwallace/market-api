from django.urls import path

from . import views

urlpatterns = [
    # products urls
    path('product/insert/', views.product_insert, name='product_insert'),
    # TODO: insert other url paths
    # path(...
    # path(...
    # path(...
]
