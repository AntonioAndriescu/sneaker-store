from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from .models import *
import datetime
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import OrderForm, CreateUserForm
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from .filters import ProductFilter

# Create your views here.

def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            #aici trimitem emailul de confirmare
            username = request.POST['username']
            email = request.POST['email']
            subject = 'Contul tau pe SneakerStore a fost inregistrat'
            message = f'Salut {username}! Bine ai venit la cel mai tare magazin de sneakers din Romania!'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            user = form.save()
            username = form.cleaned_data.get('username')
            Customer.objects.create(
                user = user,
                name = user.username,
            )
            messages.success(request, 'Contul a fost creat pentru ' + username)
            return redirect('login')

    context = {'form' : form}
    return render(request, 'store/register.html', context)

def loginPage(request):

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            user = authenticate( username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request,"Esti logat ca {username} ")
                return redirect('store')
            else:
                messages.info(request, "Username sau Parola gresite")
        else:
            messages.error(request, "Username sau Parola gresite")
    

    form = AuthenticationForm()
    context = {}
    return render(request, 'store/login.html', context)

def store(request):
    #daca user-ul este logat se poate face si salva cosul de cumparaturi in contul lui
    #daca nu este conectat nu poate adauga produse in cos

    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()

    myFilter = ProductFilter(request.GET, queryset=products)
    products = myFilter.qs

    context = {'products': products, 'cartItems': cartItems, 'myFilter': myFilter}
    return render(request, 'store/store.html', context)

def cart(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order =data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    order =data['order']
    items = data['items']


    context = {'items':items, 'order':order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.data)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('ProductId:', productId)
    return JsonResponse('Produsul a fost adaugat', safe=False)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    #testam actiunea de add sau remove si recunoasterea produsului
    print('Action:', action)
    print('ProductId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()
    #daca scadem cantitatea unui produs din cos la 0 acesta va fi eliminat
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order.complete = True

    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    #verificam daca totalul primit de la front end corespunde cu totalul din cos
    print(total)
    print(order.get_cart_total)
    if total == order.get_cart_total:
        order.complete = True
        print(order.complete)
    order.save()

     #cream obiectul shippingAdress
    ShippingAddress.objects.create(
        customer = customer,
        order = order,
        address = data['shipping']['address'],
        city = data['shipping']['city'],
        state = data['shipping']['state'],
        zipcode = data['shipping']['zipcode'],
    )

    return JsonResponse('Plata efectuata', safe=False)

