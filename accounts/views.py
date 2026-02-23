from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from accounts.forms import RegisterForm, LoginForm, ProfileForm


def register_view(request):
    """
    FBV para registrar usuario
    """
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})

def login_view(request):
    """
    FBV para loggear usuario
    """
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return redirect("/") #Sujeto a cambio dependiendo de si hacemos /home
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})

@login_required
def logout_view(request):
    """
    FBV para logout usuario
    """
    if request.method == "POST":
        logout(request)
        return redirect("/") #Sujeto a cambio dependiendo de si hacemos /home
    return render(request, "accounts/logout.html")

@login_required
def profile_view(request):
    """
    FBV para crear o editar el perfil de usuario
    """
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/profile.html", {"form": form})

