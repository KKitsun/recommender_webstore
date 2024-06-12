from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='shop_page'), name='logout'),
    path('register/', views.RegisterPage.as_view(), name='register'),
    path('', views.shop_page, name='shop_page'),
    path('cart/', views.cart, name='cart'),
    path('cart-data/', views.cart_data, name='cart-data'),
    path('checkout/', views.checkout_page, name='checkout'),
    path('game/<int:id>', views.game_page, name='game_page'),
    path('add-to-cart/', views.addItemToCart, name='add-to-cart'),
    path('change_quantity/', views.changeItemQuantity, name='change_quantity'),
    path('delete_cart_item/', views.deleteCartItem, name='delete_cart_item'),
    path('pay-test/', views.processPaymentTester, name='pay-test'),
    path('history_page/', views.history_page, name='history_page'),
    path('add-to-wishlist/', views.addItemToWishList, name='add-to-wishlist'),
    path('wishlist/', views.wishlist_page, name='wishlist'),
    path('remove-from-wishlist/', views.removeFromWishlist, name='remove-from-wishlist'),
    path('rate_game/', views.rateGame, name='rate_game'),
    path('process-payment-result/', views.processPaymentResult, name='process-payment-result'),
]
