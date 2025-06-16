from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from .models import Product, Order, PriceHistory, Review, CustomUser
from .forms import UserRegistrationForm, LoginForm, ProductForm, OrderForm, ReviewForm, BusinessLicenseForm
import pandas as pd
import requests
from django.conf import settings
from django.db.models import Sum, Avg, F
from datetime import datetime, timedelta

# 사용자 등록
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registration_complete')
        else:
            print(form.errors)  # 폼 오류 출력
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

# 회원가입 완료 뷰
def registration_complete(request):
    return render(request, 'registration/registration_complete.html')

# 로그인
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

# 로그아웃
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return render(request, 'registration/logout.html')

# 상품 목록
def product_list(request):
    query = request.GET.get('q')
    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)
    return render(request, 'shop/product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    
    # Calculate sales and price changes over the past week
    one_week_ago = datetime.now() - timedelta(days=7)
    recent_orders = Order.objects.filter(product=product, date_ordered__gte=one_week_ago)
    total_sales = recent_orders.aggregate(Sum('quantity'))['quantity__sum'] or 0
    price_changes = recent_orders.aggregate(Avg('total_price'))['total_price__avg'] or product.price
    sales_changes = recent_orders.count()

    # Check if user has purchased the product
    has_purchased = False
    if request.user.is_authenticated:
        has_purchased = Order.objects.filter(buyer=request.user, product=product).exists()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid() and has_purchased:
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        'total_sales': total_sales,
        'price_changes': price_changes,
        'sales_changes': sales_changes,
        'has_purchased': has_purchased,  # Add this line
    })

# 리뷰 수정
@login_required
def review_edit(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('product_detail', product_id=review.product.id)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'shop/review_edit.html', {'form': form})

# 상품 생성
@login_required
@user_passes_test(lambda u: u.is_seller and u.is_approved)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'shop/product_form.html', {'form': form})

# 상품 수정
@login_required
@user_passes_test(lambda u: u.is_seller and u.is_approved)
def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/product_form.html', {'form': form})

# 상품 삭제
@login_required
@user_passes_test(lambda u: u.is_seller and u.is_approved)
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('product_list')

# 장바구니 추가
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = CustomUser.objects.get(id=request.user.id)  # CustomUser 객체로 변환
    order, created = Order.objects.get_or_create(buyer=user, product=product, defaults={'quantity': 1, 'total_price': product.price})
    
    if not created:
        order.quantity += 1
        order.total_price = order.quantity * order.product.price
        order.save()
    
    return redirect('cart')

# 장바구니 보기
@login_required
def cart(request):
    user = CustomUser.objects.get(id=request.user.id)  # CustomUser 객체로 변환
    orders = Order.objects.filter(buyer=user)
    total_cost = orders.aggregate(total_cost=Sum(F('quantity') * F('product__price')))['total_cost']
    return render(request, 'shop/cart.html', {'orders': orders, 'total_cost': total_cost})

# 장바구니 업데이트
@login_required
def update_cart(request, order_id, action):
    user = CustomUser.objects.get(id=request.user.id)  # CustomUser 객체로 변환
    order = get_object_or_404(Order, id=order_id, buyer=user)
    
    if action == 'increase':
        order.quantity += 1
        order.total_price = order.quantity * order.product.price
        order.save()
    elif action == 'decrease':
        if order.quantity > 1:
            order.quantity -= 1
            order.total_price = order.quantity * order.product.price
            order.save()
        else:
            order.delete()
    elif action == 'remove':
        order.delete()
    
    return redirect('cart')

# 결제 (checkout)
@login_required
def checkout(request):
    user = CustomUser.objects.get(id=request.user.id)
    orders = Order.objects.filter(buyer=user)
    total_cost = orders.aggregate(total_cost=Sum(F('quantity') * F('product__price')))['total_cost']
    
    if request.method == 'POST':
        # 결제 처리 로직 추가 필요
        orders.delete()  # 결제 완료 후 장바구니 비우기
        return redirect('payment_success')
    
    return render(request, 'shop/checkout.html', {'total_cost': total_cost})

# 가격 동향
def price_trend(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    price_history = PriceHistory.objects.filter(product=product).order_by('date')
    df = pd.DataFrame(list(price_history.values('date', 'average_price')))
    if not df.empty:
        df['predicted_price'] = df['average_price'].rolling(window=12, min_periods=1).mean()
    else:
        df['predicted_price'] = []
    return render(request, 'shop/price_trend.html', {'product': product, 'price_history': df.to_dict('records')})

# 가격 비교
def compare_prices(request):
    strawberries = Product.objects.filter(name='strawberry')
    shine_muscats = Product.objects.filter(name='shine_muscat')
    return render(request, 'shop/compare_prices.html', {'strawberries': strawberries, 'shine_muscats': shine_muscats})

# 카테고리
def category(request):
    return render(request, 'shop/category.html')

# 판매자 랭킹
def table(request):
    return render(request, 'shop/table.html')

# 카카오페이 결제
def kakao_pay(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    url = 'https://kapi.kakao.com/v1/payment/ready'
    headers = {
        'Authorization': 'KakaoAK ' + settings.KAKAO_API_KEY,
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'cid': 'TC0ONETIME',
        'partner_order_id': order.id,
        'partner_user_id': request.user.id,
        'item_name': order.product.name,
        'quantity': order.quantity,
        'total_amount': order.total_price,
        'vat_amount': '200',
        'tax_free_amount': '0',
        'approval_url': request.build_absolute_uri('/payment/success/'),
        'fail_url': request.build_absolute_uri('/payment/fail/'),
        'cancel_url': request.build_absolute_uri('/payment/cancel/'),
    }
    response = requests.post(url, headers=headers, data=data)
    result = response.json()
    order.kakao_tid = result['tid']
    order.save()
    return redirect(result['next_redirect_pc_url'])

# 결제 성공
def payment_success(request):
    return render(request, 'shop/payment_success.html')

# 결제 실패
def payment_fail(request):
    return render(request, 'shop/payment_fail.html')

# 결제 취소
def payment_cancel(request):
    return render(request, 'shop/payment_cancel.html')

# 사용자 프로필
@login_required
def profile(request):
    user = request.user
    ranking = None
    if user.is_seller:
        sellers = CustomUser.objects.filter(is_seller=True).annotate(total_sales=Sum('products__orders__quantity')).order_by('-total_sales')
        ranking = list(sellers).index(user) + 1 if user in sellers else None
    return render(request, 'shop/profile.html', {
        'username': user.username,
        'email': user.email,
        'is_seller': user.is_seller,
        'ranking': ranking,
    })

# 구매 기록
@login_required
def purchase_history(request):
    user = request.user
    orders = Order.objects.filter(buyer=user)
    return render(request, 'shop/purchase_history.html', {'orders': orders})

# 사업자 등록증 제출
@login_required
@user_passes_test(lambda u: u.is_seller)
def submit_business_license(request):
    if request.method == 'POST':
        form = BusinessLicenseForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = BusinessLicenseForm(instance=request.user)
    return render(request, 'shop/submit_business_license.html', {'form': form})

# 바로 구매하기
@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = CustomUser.objects.get(id=request.user.id)  # CustomUser 객체로 변환
    if request.method == 'POST':
        order = Order.objects.create(
            product=product,
            buyer=user,
            quantity=1,
            total_price=product.price,
            date_ordered=datetime.now()
        )
        return redirect('payment_success')
    return redirect('product_detail', product_id=product_id)

# 판매자 랭킹
def seller_ranking(request):
    sellers = CustomUser.objects.filter(is_seller=True).annotate(total_sales=Sum('products__orders__quantity')).order_by('-total_sales')
    return render(request, 'shop/seller_ranking.html', {'sellers': sellers})
