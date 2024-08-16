from typing import Optional
from django.contrib import admin
from django.forms import ModelForm
from django.http import HttpRequest
from more_itertools import chunked

from .models import User

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    # CRUD

    fields = [
        'email',
        'telephone_prefix',
        'telephone_number',
        'is_superuser',
        'is_staff',
        'is_active',
        'groups',
        'user_permissions'
    ]

    readonly_fields = ['is_superuser']

    def save_model(self, request: HttpRequest, obj: User, form: ModelForm, change: bool):
        if change:
            obj.full_clean()
            obj.save()
        else:
            if obj.is_superuser:
                user = User.objects.create_superuser(
                    email=obj.email,
                    password=obj.password,
                    is_active=obj.is_active,
                    telephone_prefix=obj.telephone_prefix,
                    telephone_number=obj.telephone_number
                )
            else:
                user = User.objects.create_user(
                    email=obj.email,
                    telephone_prefix=obj.telephone_prefix,
                    telephone_number=obj.telephone_number,
                    is_staff=obj.is_staff,
                    is_active=obj.is_active
                )

            # we have to replace obj values to the user values
            obj.__dict__ = user.__dict__.copy()

    # VIEW/DELETE/ACTION

    list_display = [
        'email',
        'telephone',
        'is_admin',
        'is_active',
        'last_login',
        'date_joined'
    ]

    search_fields = ['email', 'telephone_number']

    @admin.display(
        boolean=True,
        description='Administrator'
    )
    def is_admin(self, user: User) -> bool:
        return user.is_superuser or user.is_staff

    @admin.display(
        description='Telephone number'
    )
    def telephone(self, user: User) -> Optional[str]:
        if user.telephone_number:
            parts = chunked(user.telephone_number, n=3)
            joined_parts = [''.join(part) for part in parts]
            formated = ' '.join(joined_parts)
            return f'(+{user.telephone_prefix}) {formated}'
        else:
            return None


admin.site.register(User, UserAdmin)
