from django.dispatch import receiver
from django.db.models import signals
from .models import User


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
            raise User.TelephoneError(
                'E-mail probably not exists - no password sent'
            )
