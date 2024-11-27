#views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def cadastro(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Você pode adicionar validações aqui
        user = User.objects.create_user(username=username, password=password)
        user.save()
        return redirect('login')
    else:
        return render(request, 'cadastro.html')

@login_required
def home_view(request):
    return render(request, 'home.html', {'user': request.user})

def login_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    if 'next' in request.GET:
        messages.warning(request, 'Você precisa estar logado para acessar esta página.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')  # Redireciona para 'home'