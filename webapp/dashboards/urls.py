from django.contrib import admin
from django.urls import path, include

from .views import index

urlpatterns = [
    path('', index, name='redirect-dashboard'),
    path('admin/', admin.site.urls),
    path('user/', include(
        ('user_dashboard.urls', 'user_dashboard'),
        namespace='user_dashboard')
    ),
]
