# python manage.py shell

from django.core.mail import send_mail
send_mail("subject", "message", "from_email@test.com", ["to_email@test.com"])
