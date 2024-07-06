from django.shortcuts import render, redirect
from django.contrib import messages
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
import json
import json
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.template import loader
import json


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

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.GET.get("next", "/create/")

        if not User.objects.filter(username=username).exists():
            return HttpResponse(
                status=401,
                headers={
                    "HX-Trigger": json.dumps({"showMessage": {"text": "Invalid Username", "type": "error"}})
                }
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return HttpResponse(
                status=401,
                headers={
                    "HX-Trigger": json.dumps({"showMessage": {"text": "Invalid Password", "type": "error"}})
                }
            )
        else:
            login(request, user)
            return HttpResponse(
                status=200,
                headers={
                    "HX-Trigger": json.dumps({
                        "showMessage": {"text": "Login successful!", "type": "success"},
                        "redirectUrl": next_url
                    })
                }
            )

    render_mode = request.GET.get("render_mode")
    template = "login_content.html" if render_mode == "content" else "login.html"

    context = {'next': request.GET.get("next", "/create/")}
    response = render(request, template, context)
    response['HX-Trigger'] = json.dumps({
        "showMessage": {
            "text": "Welcome to the login page!",
            "type": "info"
        }
    })
    return response


def register_page(request):
    if request.user.is_authenticated:
        return redirect("/create/")

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return HttpResponse(
                status=400,
                headers={
                    "HX-Trigger": json.dumps({"showMessage": {"text": "Username already taken!", "type": "error"}})
                }
            )

        user = User.objects.create_user(
            first_name=first_name, last_name=last_name, username=username
        )
        user.set_password(password)
        user.save()

        return HttpResponse(
            status=200, 
            headers={
                "HX-Trigger": json.dumps({
                    "showMessage": {"text": "Account created successfully!", "type": "success"},
                    "redirectUrl": "/auth/login/"
                })
            }
        )

    render_mode = request.GET.get("render_mode")
    template = "register_content.html" if render_mode == "content" else "register.html"

    context = {}
    response = render(request, template, context)
    response['HX-Trigger'] = json.dumps({
        "showMessage": {
            "text": "Welcome to the registration page!",
            "type": "info"
        }
    })
    return response


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return HttpResponse(
            status=205, 
            headers={
                "HX-Trigger": json.dumps({
                    "showMessage": {"text": "Successfully Logged Out.", "type": "success"},
                    "redirectUrl": "/" 
                })
            }
        )
    return HttpResponse(status=405)
