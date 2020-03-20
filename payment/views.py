from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

import braintree
import weasyprint
from io import BytesIO

from orders.models import Order


def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # retrieve nonce
        nonce = request.POST.get('payment_method_nonce', None)
        # create and submit transaction
        result = braintree.Transaction.sale({
            'amount': f'{order.get_total_cost():.2f}',
            'payment_method_nonce': nonce,
            'options': {'submit_for_settlement': True}
        })
        if result.is_success:
            # mark the order as paid
            order.paid = True
            # store transaction id in the order
            order.braintree_id = result.transaction.id
            order.save()

            # create e-mail message
            subject = f'My shop - Invoice no. {order.id}'
            message = 'Please, find attached the invoice for your recent purchase.'
            email = EmailMessage(subject, message, 'admin@myshop.com', [order.email])

            # generate pdf
            html = render_to_string('orders/order/pdf.html', {'order': order})
            out = BytesIO()
            stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
            weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

            # attach pdf to mail
            email.attach(f'order_{order.id}', out.getvalue(), 'application/pdf')

            # send mail
            email.send()

            return redirect('payment:done')
        else:
            return redirect('payment:canceled')
    else:
        # generate nonce for JavaScript SDK
        client_token = braintree.ClientToken.generate()
        return render(request, 'payment/process.html', {'order': order, 'client_token': client_token})


def payment_done(request):
    return render(request, 'payment/done.html')


def payment_canceled(request):
    return render(request, 'payment/canceled.html')
