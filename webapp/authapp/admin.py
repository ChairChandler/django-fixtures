from django.contrib import admin

from .models import AppUser

# Register your models here.


class AppUserAdmin(admin.ModelAdmin):
    fields = ['email', 'password', 'telephone_prefix', 'telephone_number']


admin.site.register(AppUser, AppUserAdmin)
