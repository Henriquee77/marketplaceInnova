from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ativo, Transacao, Portfolio, Saldo
from decimal import Decimal 
from django.db.models import F


def cadastro(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        saldo_inicial = Decimal(request.POST['saldo_inicial'])  # Garantindo que o saldo seja do tipo Decimal

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Usuário já existe.')
            return redirect('cadastro')

        # Cria o usuário
        user = User.objects.create_user(username=username, password=password)
        user.save()

        # Cria o saldo inicial do usuário
        Saldo.objects.create(usuario=user, saldo_disponivel=saldo_inicial)

        messages.success(request, 'Cadastro realizado com sucesso! Faça login.')
        return redirect('login')

    return render(request, 'cadastro.html')



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

@login_required
def home_view(request):
    saldo_virtual = request.session.get('saldo_virtual', 100000)
    saldo_virtual = float(saldo_virtual)  # Converte para float, se necessário

    portfolio = Portfolio.objects.filter(usuario=request.user)

    # Calcula o saldo investido
    saldo_investido = sum(item.valor_total for item in portfolio)
    saldo_investido = float(saldo_investido)  # Converte para float

    ativos = Ativo.objects.all()

    # Convertendo os preços dos ativos para float
    ativos_info = []
    for ativo in ativos:
        ativos_info.append({
            'nome': ativo.nome,
            'preco': float(ativo.preco),  # Convertendo o preço para float
            'descricao': ativo.descricao,
        })

    return render(request, 'home.html', {
        'saldo_virtual': saldo_virtual,
        'saldo_investido': saldo_investido,
        'ativos': ativos_info,  # Passando a lista de ativos com preços convertidos
    })

@login_required
def atualizar_simulacao(request):
    if request.method == 'POST':
        # Aqui, você pode definir o percentual de valorização
        # Exemplo de valorização de 5%
        percentual_valorizacao = 5  # Este valor pode vir de um formulário ou ser alterado diretamente no código

        ativos = Ativo.objects.all()  # Obtém todos os ativos
        for ativo in ativos:
            # Calcula o novo preço com base na valorização
            novo_preco = ativo.simular_valorizacao(percentual_valorizacao)
            ativo.preco = novo_preco
            ativo.save()  # Atualiza o preço do ativo

        messages.success(request, 'Simulação de ativos atualizada com sucesso!')
        return redirect('home')  # Redireciona de volta para a página inicial

    # Caso a requisição não seja POST, apenas redireciona
    return redirect('home') # Redireciona de volta para a página inicial



@login_required
def comprar_ativo(request, ativo_id):
    ativo = get_object_or_404(Ativo, id=ativo_id)

    # Garantir que o saldo_virtual está na sessão como Decimal
    saldo_virtual = Decimal(request.session.get('saldo_virtual', 100000))  # Define saldo virtual inicial

    if request.method == 'POST':
        # Verifica se a quantidade foi informada e é válida
        try:
            quantidade = int(request.POST['quantidade'])
            if quantidade <= 0:
                raise ValueError('A quantidade deve ser maior que zero.')
        except (ValueError, TypeError):
            messages.error(request, 'Quantidade inválida. Por favor, insira um número positivo.')
            return redirect('pagina_comprar')  # Redireciona de volta à página de compra

        # Calcula o total do preço
        total_preco = Decimal(quantidade) * ativo.preco  # Garantindo que a multiplicação é feita entre Decimal

        # Verifica se o saldo é suficiente para a compra
        if total_preco > saldo_virtual:
            messages.error(request, 'Saldo insuficiente para realizar a compra.')
            return redirect('pagina_comprar')  # Redireciona de volta à página de compra

        # Atualiza o saldo disponível na sessão
        request.session['saldo_virtual'] = float(saldo_virtual - total_preco)  # Atualiza o saldo na sessão como float

        # Registra a transação de compra
        Transacao.objects.create(
            usuario=request.user,
            ativo=ativo,
            tipo='compra',
            quantidade=quantidade,
            preco_unitario=ativo.preco,
            valor_total=total_preco,  # Registrando o valor total da compra
        )

        # Atualiza ou cria o portfólio
        portfolio, created = Portfolio.objects.get_or_create(
            usuario=request.user, ativo=ativo,
            defaults={'quantidade': 0, 'valor_total': 0}
        )

        # Atualiza a quantidade e o valor total no portfólio
        portfolio.quantidade += quantidade  # Atualiza de forma eficiente
        portfolio.valor_total += total_preco  # Atualiza o valor total de forma eficiente
        portfolio.save()

        messages.success(request, f'Compra de {quantidade} {ativo.nome} realizada com sucesso.')
        return redirect('home')  # Redireciona para a página inicial ou qualquer outra

    return render(request, 'comprar.html', {'ativo': ativo})



@login_required
def vender_ativo(request, ativo_id):
    ativo = get_object_or_404(Ativo, id=ativo_id)
    portfolio = Portfolio.objects.filter(usuario=request.user, ativo=ativo).first()

    # Verifica se o usuário possui o ativo no portfólio
    if not portfolio or portfolio.quantidade == 0:
        messages.error(request, f'Você não possui {ativo.nome} para vender.')
        return redirect('home')

    if request.method == 'POST':
        try:
            quantidade = int(request.POST['quantidade'])
        except ValueError:
            messages.error(request, 'Quantidade inválida.')
            return redirect('pagina_vender')

        # Verifica se a quantidade de venda é maior que a quantidade no portfólio
        if quantidade > portfolio.quantidade:
            messages.error(request, 'Quantidade insuficiente para realizar a venda.')
            return redirect('pagina_vender')

        total_preco = quantidade * ativo.preco

        # Atualiza o saldo disponível
        saldo = Saldo.objects.get(usuario=request.user)
        saldo.saldo_disponivel += total_preco
        saldo.save()

        # Registra a transação de venda
        Transacao.objects.create(
            usuario=request.user,
            ativo=ativo,
            tipo='venda',
            quantidade=quantidade,
            preco_unitario=float(ativo.preco)
        )

        # Atualiza o portfólio
        portfolio.quantidade -= quantidade
        portfolio.valor_total -= total_preco
        if portfolio.quantidade == 0:
            portfolio.delete()
        else:
            portfolio.save()

        messages.success(request, f'Venda de {quantidade} {ativo.nome} realizada com sucesso.')
        return redirect('home')

    return render(request, 'vender.html', {'ativo': ativo, 'portfolio': portfolio})


@login_required
def historico_view(request):
    historico = Transacao.objects.filter(usuario=request.user).order_by('-data')
    return render(request, 'historico.html', {'historico': historico})


@login_required
def relatorios_view(request):
    transacoes = Transacao.objects.filter(usuario=request.user)

    total_investido = sum(t.preco_unitario * t.quantidade for t in transacoes if t.tipo == 'compra')
    total_vendido = sum(t.preco_unitario * t.quantidade for t in transacoes if t.tipo == 'venda')
    saldo_atual = total_investido - total_vendido

    portfolio = Portfolio.objects.filter(usuario=request.user)
    saldo_investido = sum(item.valor_total for item in portfolio)

    contexto = {
        'transacoes': transacoes,
        'total_investido': total_investido,
        'total_vendido': total_vendido,
        'saldo_disponivel': saldo_atual,
        'saldo_investido': saldo_investido,
        'portfolio': portfolio,
    }
    return render(request, 'relatorios.html', contexto)


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def pagina_comprar(request):
    ativos = Ativo.objects.all()
    return render(request, 'comprar.html', {'ativos': ativos})


@login_required
def pagina_vender(request):
    portfolio = Portfolio.objects.filter(usuario=request.user)
    return render(request, 'vender.html', {'portfolio': portfolio})
