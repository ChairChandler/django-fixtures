from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    path('home', TemplateView.as_view(template_name='home.html'), name='index')
]
