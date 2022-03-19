from django.urls import path
from . import views


urlpatterns = [
    path('customer/register/', views.register_user, name='index'),
]

