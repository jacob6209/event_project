from allauth.account.forms import LoginForm
from django import forms




class CustomLoginForm(LoginForm):
   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].label = "نام کاربری یا ایمیل"
        self.fields['password'].label = "کلمه عبور"

        # Optional placeholders
        self.fields['login'].widget.attrs['placeholder'] = "کد ملی "
        self.fields['password'].widget.attrs['placeholder'] = "کلمه عبور"

         # Change the label for 'remember' field
        self.fields['remember'].label = "مرا به خاطر بسپار"
        
         # REMOVE the default help_text that adds "Forgot your password?"
        self.fields['password'].help_text = None