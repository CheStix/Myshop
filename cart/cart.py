from decimal import Decimal
from django.conf import settings

from shop.models import Product


class Cart(object):
    def __init__(self, request):
        """Initialization cart object"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save empty cart in session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def __iter__(self):
        """iterate over items in cart and get products from database"""
        product_id = self.cart.keys()
        # get objects from model Product and add them to cart
        products = Product.objects.filter(id__in=product_id)

        cart = self.cart.copy()
        for product in products:
            cart[str(product_id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """return count products in cart"""
        return sum(item['quantity'] for item in self.cart.values())

    def add(self, product, quantity=1, update_quantity=False):
        """ add product in cart or update quantity"""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # mark session as 'modified'
        self.session.modified = True

    def remove(self, product):
        """remove product from cart"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # clear cart
        del self.session[settings.CART_SESSION_ID]
        self.save()
