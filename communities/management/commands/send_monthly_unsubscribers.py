from django.core.management.base import BaseCommand
from django.utils import translation

from users.utils import send_monthly_unsubscribe_emails


class Command(BaseCommand):
    help = 'Send unsubscribers monthly'

    def handle(self, *args, **options):
        from django.conf import settings
        translation.activate(settings.LANGUAGE_CODE)
        send_monthly_unsubscribe_emails()
        translation.deactivate()
