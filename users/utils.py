from django.core.mail import send_mail
from django.utils import timezone


def send_monthly_unsubscribe_emails():
    from .models import UnsubscribeUser
    dt = timezone.now()
    lm = dt - 1
    users = UnsubscribeUser.objects.filter(created_at__month=lm, created_at__year=dt.year)

    if users:
        from_email = "no-reply <opencommittee.co.il>"
        send_mail(
            'Monthly unsubscribers list',
            ', '.join([x.email for x in users]),
            from_email,
            ['aharon.porath@gmail.com'],
            fail_silently=False,
        )
