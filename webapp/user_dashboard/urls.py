from django.urls import path, include
import views

urlpatterns = [
    path('', views.redirect_to_current_calendar, name='index'),
    path('/<str:calendar_id>', views.show_calendar, name='calendar'),
    path('reservation/join/<str:reservation_id>',
         views.check_reservation_participant, name='reservation_join')
]
