from django import forms
from docker.models import User



class login(forms.ModelForm):
    """
        Login form
        Attributes:
            email {str}
                this attribute is the user's identifier
            password {str}
                this attribute is the key to a user's session
    """
    email = forms.EmailField(max_length=60)
    password = forms.PasswordInput()
    class Meta:
        model = User
        fields = [
            'email',
            'password',
        ]