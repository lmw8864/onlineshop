# python manage.py shell
# from django.core.mail import send_mail
# send_mail("subject", "message", "from_email@test.com", ["to_email@test.com"])


from celery import task
from django.core.mail import send_mail
from .models import Order


@task
def order_created(order_id):
    order = Order.objects.get(id=order_id)
    subject = 'Order Num.{}'.format(order.id)
    message = 'Dear {}, You have successfully placed an order. Your oder id is {}.'.format(order.first_name, order.id)
    mail_sent = send_mail(subject, message, 'myemail@test.com', [order.email])

    return mail_sent
