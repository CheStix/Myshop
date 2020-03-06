from celery import task

from django.core.mail import send_mail

from .models import Order


@task
def order_created(order_id):
    """task to sent email notification when order successfully created"""
    order = Order.objects.get(id=order_id)
    subject = f'Order №{order.id}'
    message = f'Dear {order.first_name},\n\nYou have successfully placed an order. Your order id is {order.id}'
    print('*************log*********')
    mail_sent = send_mail(subject, message, 'admin@myshop.com', [order.email])
    print('*************end*********')
    return mail_sent
    # print('*********************************')
