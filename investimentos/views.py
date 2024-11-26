from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


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

def login_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Substitua 'home' pela sua página após login
        else:
            return render(request, 'login.html', {'error': 'Usuário ou senha inválidos'})
    else:
        return render(request, 'login.html')
    
@login_required
def home_view(request):
    return render(request, 'home.html', {'user': request.user})
