import json
from .models import *


def cookieCart(request):
    #actualizam cantitatea din cos in functie de cookie - pentru useri neautentificati
    #cream o exceptie pentru cazul in care cookie-ul "cart" este sters
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    print('Cart:', cart)
    items = []
    order = {'get_cart_total':0, 'get_cart_items':0}
    cartItems = order['get_cart_items']

    for i in cart:
        #daca stergem un produs din baza de date care este deja in cosul de cumparaturi al unui guest, ii vom face pass la lista produselor din cos
        try:
            cartItems += cart[i]["quantity"]

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]["quantity"])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]["quantity"]

            #pt fiecare item din cart - utilizator neautentificat
            #pt a nu fi nevoie sa le stocam in baza de date ca order-urile pentru useri autentificati
            item = {

                'product' : {
                    'id' : product.id,
                    'name' : product.name,
                    'price' : product.price,
                    'imageURL' : product.imageURL,

                },
                'quantity' : cart[i]["quantity"],
                'get_total' : total
            }
            items.append(item)
        except:
            pass
    return{'cartItems':cartItems, 'order':order, 'items':items}

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    return{'cartItems':cartItems, 'order':order, 'items':items}

def guestOrder(request, data):

    print('User is not logged in..')

    print('COOKIES:', request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        email = email,
    )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer = customer,
        complete = False,
    )

    for item in items:
        product = Product.objects.get(id = item['product']['id'])

        orderItem = OrderItem.objects.create(
            product = product, 
            order = order,
            quantity = item['quantity']
        )

    return customer, order