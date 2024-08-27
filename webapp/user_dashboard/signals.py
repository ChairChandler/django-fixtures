from django.dispatch import receiver
from django.db.models import signals
from .models import ReservationUnit


@receiver(signals.pre_save, sender=ReservationUnit)
def check_reservation_participant(sender, instance: ReservationUnit, **kwargs):
    old_instance = ReservationUnit.objects.get(pk=instance.pk)
    if all([
            old_instance.participant is not None,
            old_instance.participant != instance.participant
    ]):
        raise ReservationUnit.ReservationError(
            'Cannot change participant if another already set.'
        )
