from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Product, Order, Review

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'is_seller']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['quantity']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={'maxlength': 30}),
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)])
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) > 30:
            raise forms.ValidationError('리뷰는 30자를 넘을 수 없습니다.')
        return content

class BusinessLicenseForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['business_license']
        widgets = {
            'business_license': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
