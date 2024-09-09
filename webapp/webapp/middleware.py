from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect

from accounts.models import User


class UserRedirectMiddleware(MiddlewareMixin):
    '''
    Redirect anonymous user to login page.
    Redirect admin on login, user, index path to admin page.
    Redirect user on login, admin, index path to user page.
    '''
    index_path = reverse('index')
    login_path = reverse('accounts:login')
    admin_panel_path = reverse('admin:index')
    user_panel_path = reverse('user_dashboard:index')

    def process_view(self, request: WSGIRequest, view_func, view_args, view_kwargs):
        user: User = request.user  # type: ignore

        is_anonymous = (not user.is_authenticated)
        is_admin = (user.is_staff or user.is_superuser)

        is_on_index_path = (request.path == self.index_path)
        is_on_user_path = (request.path == self.user_panel_path)
        is_on_admin_path = (request.path == self.admin_panel_path)
        is_on_login_path = (request.path == self.login_path)

        if is_anonymous:
            if not is_on_login_path:
                return redirect(self.login_path)
        elif is_admin:
            if any([
                is_on_index_path,
                is_on_user_path,
                is_on_login_path
            ]):
                return redirect(self.admin_panel_path)
        else:
            if any([
                is_on_index_path,
                is_on_admin_path,
                is_on_login_path
            ]):
                return redirect(self.user_panel_path)
