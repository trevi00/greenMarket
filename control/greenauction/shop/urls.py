from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.product_list, name='home'),
    path('register/', views.register, name='register'),
    path('registration_complete/', views.registration_complete, name='registration_complete'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('purchase_history/', views.purchase_history, name='purchase_history'),
    path('submit_business_license/', views.submit_business_license, name='submit_business_license'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:product_id>/edit/', views.product_update, name='product_update'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/<int:order_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('price_trend/<int:product_id>/', views.price_trend, name='price_trend'),
    path('compare_prices/', views.compare_prices, name='compare_prices'),
    path('kakao_pay/<int:order_id>/', views.kakao_pay, name='kakao_pay'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/fail/', views.payment_fail, name='payment_fail'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('table/', views.table, name='table'),
    path('category/', views.category, name='category'),
    path('buy_now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('seller_ranking/', views.seller_ranking, name='seller_ranking'),
    path('password_reset/', include('django.contrib.auth.urls')),
    path('review/edit/<int:review_id>/', views.review_edit, name='review_edit'),  # 추가된 경로
]
