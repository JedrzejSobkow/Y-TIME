from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    
    class Meta:
        
        model = User
        
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "password1",
            "password2"
        ]
        
    
    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("User with this email already exists")
        
        return email
        
    def save(self, commit = True):
        user = super().save(commit=False)
        
        email = self.cleaned_data["email"].lower()
        user.email = email
        
        if commit:
            user.save()
            
        return user