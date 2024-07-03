from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse


def home_page(request):
    if request.user.is_authenticated:
        if request.GET.get("render_mode") == "content":
            return render(request, "home_content.html")
        return redirect("/create/")
    if request.GET.get("render_mode") == "content":
        return render(request, "home_content.html")

    return render(request, "home.html")


# Define a view function for the login page


def login_page(request):
    if request.user.is_authenticated:
        return redirect("/create/")

    # Check if the HTTP request method is POST (form submission)
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.GET.get("next", "/create/")

        # Check if a user with the provided username exists
        if not User.objects.filter(username=username).exists():
            # Display an error message if the username does not exist
            messages.error(request, "Invalid Username")
            return redirect("/auth/login/")

        # Authenticate the user with the provided username and password
        user = authenticate(username=username, password=password)

        if user is None:
            # Display an error message if authentication fails (invalid password)
            messages.error(request, "Invalid Password")
            return redirect("/auth/login/")
        else:
            # Log in the user and redirect to the home page upon successful login
            login(request, user)
            return HttpResponseRedirect(next_url)

    # Render the login page template (GET request)
    if request.GET.get("render_mode") == "content":
        return render(request, "login_content.html")
    return render(request, "login.html")


# Define a view function for the registration page
def register_page(request):
    if request.user.is_authenticated:
        return redirect("/create/")

    # Check if the HTTP request method is POST (form submission)
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check if a user with the provided username already exists
        user = User.objects.filter(username=username)

        if user.exists():
            # Display an information message if the username is taken
            messages.info(request, "Username already taken!")
            return redirect("/auth/register/")

        # Create a new User object with the provided information
        user = User.objects.create_user(
            first_name=first_name, last_name=last_name, username=username
        )

        # Set the user's password and save the user object
        user.set_password(password)
        user.save()

        # Display an information message indicating successful account creation
        messages.info(request, "Account created Successfully!")
        return render(request, "login_content.html")

    # Render the registration page template (GET request)
    if request.GET.get("render_mode") == "content":
        return render(request, "register_content.html")
    return render(request, "register.html")


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("/auth/")
    return HttpResponse(status=405)
