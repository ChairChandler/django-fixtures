from django.urls import path, include
from .views import *

urlpatterns = [
    path('', redirect_to_current_calendar, name='index'),
    path('<str:calendar_id>', show_calendar, name='calendar'),
    path('reservation/join/<str:reservation_id>',
         join_reservation, name='reservation_join')
]
