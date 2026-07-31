from decimal import Decimal

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from food.models import Food
from .models import Order, OrderItem

User = get_user_model()


class AccountForm(forms.Form):
    full_name = forms.CharField(
        label='Full name',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Jane Doe'})
    )
    email = forms.EmailField(
        label='Email address',
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user is not None and not self.is_bound:
            full_name = ' '.join(filter(None, [user.first_name, user.last_name]))
            self.fields['full_name'].initial = full_name
            self.fields['email'].initial = user.email

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if User.objects.exclude(pk=self.user.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

    def save(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if full_name:
            first_name, *last_parts = full_name.split(' ', 1)
            last_name = last_parts[0] if last_parts else ''
        else:
            first_name = ''
            last_name = ''

        self.user.first_name = first_name
        self.user.last_name = last_name
        self.user.email = self.cleaned_data.get('email', '')
        self.user.save()
        return self.user


def get_cart(request):
    return request.session.get('cart', {})


def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def cart_json_response(request, message='', success=True, status=200):
    cart_items, subtotal, total_qty = cart_data(request)
    items = [
        {
            'id': item['food'].pk,
            'name': item['food'].name,
            'quantity': item['quantity'],
            'unit_price': str(item['food'].price),
            'line_total': str(item['line_total']),
        }
        for item in cart_items
    ]
    return JsonResponse({
        'success': success,
        'message': message,
        'cart': {
            'items': items,
            'subtotal': str(subtotal),
            'total_qty': total_qty,
        },
    }, status=status)


def cart_data(request):
    cart = get_cart(request)
    items = []
    subtotal = Decimal('0.00')
    total_qty = 0

    for item_id, quantity in cart.items():
        try:
            food = Food.objects.get(pk=item_id)
        except Food.DoesNotExist:
            continue

        quantity = int(quantity)
        line_total = food.price * quantity
        items.append({'food': food, 'quantity': quantity, 'line_total': line_total})
        subtotal += line_total
        total_qty += quantity

    return items, subtotal, total_qty


def global_context(request):
    _, subtotal, total_qty = cart_data(request)
    return {'cart_qty': total_qty, 'cart_total': subtotal}


def home_view(request):
    food_items = Food.objects.all()
    context = {'food_items': food_items}
    context.update(global_context(request))
    return render(request, 'home/home.html', context)


def food_detail_view(request, pk):
    food = get_object_or_404(Food, pk=pk)
    context = {'food': food}
    context.update(global_context(request))
    return render(request, 'home/food_detail.html', context)


def add_to_cart(request, pk):
    if request.method != 'POST':
        return redirect('food_detail', pk=pk)

    food = get_object_or_404(Food, pk=pk)
    cart = get_cart(request)
    item_key = str(pk)
    cart[item_key] = cart.get(item_key, 0) + 1
    save_cart(request, cart)

    if is_ajax(request):
        return cart_json_response(request, f'{food.name} added to cart.')

    messages.success(request, f'{food.name} added to cart.')
    next_url = request.POST.get('next') or reverse('food_detail', kwargs={'pk': pk})
    return redirect(next_url)


def remove_from_cart(request, pk):
    if request.method != 'POST':
        return redirect('cart')

    cart = get_cart(request)
    cart.pop(str(pk), None)
    save_cart(request, cart)

    if is_ajax(request):
        return cart_json_response(request, 'Item removed from your cart.')

    messages.info(request, 'Item removed from your cart.')
    return redirect('cart')


def update_cart(request, pk):
    if request.method != 'POST':
        return redirect('cart')

    cart = get_cart(request)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity <= 0:
        cart.pop(str(pk), None)
        message = 'Item removed from your cart.'
    else:
        cart[str(pk)] = quantity
        message = 'Cart updated successfully.'

    save_cart(request, cart)

    if is_ajax(request):
        return cart_json_response(request, message)

    if quantity <= 0:
        messages.info(request, message)
    else:
        messages.success(request, message)

    return redirect('cart')


def cart_view(request):
    cart_items, subtotal, total_qty = cart_data(request)
    context = {'cart_items': cart_items, 'subtotal': subtotal, 'total_qty': total_qty}
    context.update(global_context(request))
    return render(request, 'home/cart.html', context)


@login_required(login_url='login')
def checkout_view(request):
    cart_items, subtotal, total_qty = cart_data(request)
    if not cart_items:
        messages.warning(request, 'Your cart is empty. Add a meal before checkout.')
        return redirect('home')

    default_name = request.user.get_full_name() or request.user.username
    default_email = request.user.email

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip() or default_name
        customer_email = request.POST.get('customer_email', '').strip() or default_email
        customer_address = request.POST.get('customer_address', '').strip()

        if not customer_address:
            messages.error(request, 'Please provide a delivery address.')
            context = {
                'cart_items': cart_items,
                'subtotal': subtotal,
                'total_qty': total_qty,
                'default_name': customer_name,
                'default_email': customer_email,
            }
            context.update(global_context(request))
            return render(request, 'home/checkout.html', context)

        order = Order.objects.create(
            user=request.user,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_address=customer_address,
            total=subtotal,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                food=item['food'],
                quantity=item['quantity'],
                price=item['food'].price,
            )

        request.session.pop('cart', None)
        messages.success(request, 'Your order has been placed successfully.')
        return render(request, 'home/order_success.html', {
            'customer_name': customer_name,
            'subtotal': subtotal,
            'total_qty': total_qty,
            'order': order,
        })

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total_qty': total_qty,
        'default_name': default_name,
        'default_email': default_email,
    }
    context.update(global_context(request))
    return render(request, 'home/checkout.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required(login_url='login')
def order_history_view(request):
    selected_status = request.GET.get('status', '')
    orders = Order.objects.filter(user=request.user)

    if selected_status:
        orders = orders.filter(status=selected_status)

    orders = orders.prefetch_related('items__food')
    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'selected_status': selected_status,
    }
    context.update(global_context(request))
    return render(request, 'home/order_history.html', context)


@login_required(login_url='login')
def profile_view(request):
    if request.method == 'POST':
        form = AccountForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account details have been updated.')
            return redirect('account')
    else:
        form = AccountForm(user=request.user)

    context = {'form': form}
    context.update(global_context(request))
    return render(request, 'home/account.html', context)


@login_required(login_url='login')
def reorder_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    cart = {}

    for item in order.items.all():
        if item.food is None:
            continue
        cart[str(item.food.pk)] = cart.get(str(item.food.pk), 0) + item.quantity

    save_cart(request, cart)
    messages.success(request, 'Your previous order has been added to the cart.')
    return redirect('cart')


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your account is ready.')
            return redirect('home')
    else:
        form = UserCreationForm()

    context = {'form': form}
    context.update(global_context(request))
    return render(request, 'home/signup.html', context)
