from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^create/$', views.order_create, name='order_create'),
    url(r'^complete/$', views.order_complete, name='order_complete'),
]
