from django.dispatch import receiver
from django.db.models import signals
from .models import User


@receiver(signals.post_save, sender=User)
def validate_telephone(sender, instance: User, created, **kwargs):
    "Telephone cannot not be empty for normal user during account creation."
    if created:
        is_admin = (instance.is_superuser or instance.is_staff)
        if instance.telephone_number is None and not is_admin:
            raise User.TelephoneError(
                'Telephone number cannot be empty for normal user during creation'
            )


@receiver(signals.post_save, sender=User)
def send_mail_with_password(sender, instance: User, created, **kwargs):
    if created:
        pwd = getattr(instance, '_password')
        is_email_sent = instance.email_user_with_status(
            'Account created',
            f'Password: {pwd}',
            from_email='test@mail.com',
            fail_silently=False
        )

        if not is_email_sent:
            instance.delete()
            raise User.EmailError(
                'E-mail probably not exists - no password sent'
            )
