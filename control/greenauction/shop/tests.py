from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Product, Review

class ShopTests(TestCase):

    def setUp(self):
        # 유저 생성
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        
        # 상품 생성
        self.product = Product.objects.create(name='strawberry', description='Fresh strawberries', price=10.00, seller=self.user)

    def test_product_list_view(self):
        # 상품 리스트 페이지 테스트
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_product_detail_view(self):
        # 상품 상세 페이지 테스트
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_user_registration(self):
        # 회원 가입 테스트
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!',
        })
        self.assertEqual(response.status_code, 302)  # 리다이렉션 확인
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_add_review(self):
        # 리뷰 추가 테스트
        review_data = {
            'rating': 5,
            'comment': 'Great strawberries!'
        }
        response = self.client.post(reverse('product_detail', args=[self.product.id]), review_data)
        self.assertEqual(response.status_code, 302)  # 리뷰 추가 후 리다이렉션 확인
        self.assertTrue(Review.objects.filter(product=self.product, user=self.user, comment='Great strawberries!').exists())

    def test_search_product(self):
        # 상품 검색 테스트
        response = self.client.get(reverse('product_list'), {'q': 'strawberry'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
