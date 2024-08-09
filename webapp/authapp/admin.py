from django.contrib import admin

from .models import AppUser, Telephone

# Register your models here.


class TelephoneInline(admin.StackedInline):
    model = Telephone


class AppUserAdmin(admin.ModelAdmin):
    fields = ['email', 'password']
    inlines = [TelephoneInline]


admin.site.register(AppUser, AppUserAdmin)
