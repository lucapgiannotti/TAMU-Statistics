from django.urls import path
from .views import form_view

from django.urls import path
from .views import form_view

urlpatterns = [
    path('submit/', form_view, name='form_view'),
]