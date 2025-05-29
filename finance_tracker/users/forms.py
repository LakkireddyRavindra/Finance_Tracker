from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = CustomUser
        fields = ('username','email', 'phone_number', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        
        if commit:
            user.save()
        return user

from django.core.exceptions import ValidationError

def clean_username(self):
    username = self.cleaned_data.get('username')
    
    # 👉 Add the duplicate check logic here:
    if CustomUser.objects.filter(username=username).exists():
        raise ValidationError("This username is already taken. Please choose another.")
    
    return username
def clean_email(self):
    email = self.cleaned_data.get('email')
    if CustomUser.objects.filter(email=email).exists():
        raise ValidationError("Email already registered.")
    return email