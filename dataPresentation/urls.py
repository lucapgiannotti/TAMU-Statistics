from django.urls import path
from .views import data_presentation_view

urlpatterns = [
    path('', data_presentation_view, name='data_presentation'),
]