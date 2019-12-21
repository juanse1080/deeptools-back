from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from module import views, models

def template(request):
    """ 
        This method redirects to a view depending on the active session
        Redirect: 
            {Template} registration/login.html
                if there is no sessio
                
            {View} board
               if there is session  
    """
    if request.user.is_authenticated:
        return redirect(views.create_docker)
    else:
        if request.method == 'POST':
            user = auth(request)
            if user is not None:
                login(request, user)
                return redirect(views.create_docker)
            messages.error(request, 'Credenciales incorrectas.')
        return render(request, 'login.html')

@login_required
def logout_view(request):
    """ 
        This method clears session data
        Redirect: 
            template {Function}
                
    """

    logout(request)
    return redirect(template)

def auth(request):
    """ 
        This method performs the authentication of the user found
        Return: 
            {boolean}
                Transaction status
            {None}
    """
    login_valid = get_user(email=request.POST['email'])
    pwd_valid = check_password(request.POST['password'], login_valid.password if login_valid else None)
    if login_valid and pwd_valid:
        return login_valid
    return None
        
def get_user(email):
    """ 
        This method returns the user found with the email provided, in case of not finding it will return None
        Return: 
            {User}
                User found
            {None}
    """
    try:
        return models.User.objects.get(email=email)
    except models.User.DoesNotExist:
        return None