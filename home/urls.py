from django.urls import path
from django.contrib.auth.views import LoginView

from .views import (
    add_to_cart,
    cart_view,
    checkout_view,
    food_detail_view,
    home_view,
    logout_view,
    order_history_view,
    profile_view,
    reorder_view,
    remove_from_cart,
    signup_view,
    update_cart,
)

urlpatterns = [
    path('', home_view, name='home'),
    path('food/<int:pk>/', food_detail_view, name='food_detail'),
    path('cart/add/<int:pk>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:pk>/', update_cart, name='update_cart'),
    path('cart/', cart_view, name='cart'),
    path('checkout/', checkout_view, name='checkout'),
    path('account/', profile_view, name='account'),
    path('orders/', order_history_view, name='order_history'),
    path('orders/<int:pk>/reorder/', reorder_view, name='reorder'),
    path('signup/', signup_view, name='signup'),
    path('login/', LoginView.as_view(template_name='home/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
]
