from django.apps import AppConfig


class UserDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_dashboard'

    def ready(self) -> None:
        import user_dashboard.signals
