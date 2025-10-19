from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    # Home page showing list of devices
    path('', views.device_list, name='device_list'),
    # Device detail page
    path('device/<slug:slug>/', views.device_detail, name='device_detail'),
    # Checkout page for a specific device
    path('checkout/<slug:slug>/', views.checkout, name='checkout'),
    # About page
    path('about/', views.about, name='about'),
    # Contact page
    path('contact/', views.contact, name='contact'),

]