from django.views import View
from user.forms import SignUpForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

class SignUp(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})
    def post(self, request):
        form = SignUpForm(request.POST)
        #emailExist=True
        #usernameExist=True
        if form.is_valid() == True:
            fs=form.save(commit=False)
            uservalue = form.cleaned_data.get('username')
            passwordvalue = form.cleaned_data.get('password')
            emailvalue = form.cleaned_data.get('email')
            try:
                user = User.objects.get(username=uservalue)
                return render(request, 'signup.html', {'form': form})
            except User.DoesNotExist:
                usernameExist=False
            try:
                email = User.objects.get(email=emailvalue)
                emailExist = True
                context = {'form': form,
                           'email': email}
                return render(request, 'signup.html', context)
            except User.DoesNotExist:
                emailExist=False
            if emailExist==False and usernameExist==False:
                user = User.objects.create_user(uservalue, password=passwordvalue, email=emailvalue)
                user.save()
                message = "Registered succesfully"
                login(request, user)
                return redirect("index")
        if form.is_valid() == False:
            userMessage = "This username has been taken"
            return render(request, 'signup.html', {'form': form, 'userMessage': userMessage}, status=200)

class SignIn(View):
    def get(self, request):
        return render(request, 'signin.html')
    def post(self, request):
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        nextTo = request.GET.get('next', reverse("index"))
        user = authenticate(username=username, email=email, password=password)

        if user is not None and user.is_active:
            login(request, user)
            print(user.password)
            return HttpResponseRedirect(nextTo)
        else:
            messages.add_message(request, messages.ERROR, "Invalid username or password")
            return HttpResponseRedirect(reverse("signin"))


def signout(request):
    logout(request)
    return redirect("index")


class EditProfile(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, "editprofile.html")
        else:
            return HttpResponseRedirect(reverse("signup"))

    def post(self, request):
        emailExist = True
        user=request.user
        emailvalue = request.POST["email"]
        passwordvalue = request.POST.get("password", "")
        try:
            email = User.objects.get(email=emailvalue)
            return render(request, 'editprofile.html')
        except User.DoesNotExist:
            emailExist = False
            if emailExist==False:
                user.email = emailvalue
                if passwordvalue!= "":
                    user.set_password(passwordvalue)
                user.save()
                login(request, user)
                return redirect("index")
            else:
                return render(request, 'editprofile.html')