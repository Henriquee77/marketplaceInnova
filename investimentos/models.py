from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal  # Importando o Decimal para evitar problemas de multiplicação

class Ativo(models.Model):
    """Representa um ativo financeiro disponível no marketplace"""
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)  # Exemplo: 1000.50
    descricao = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    def simular_valorizacao(self, percentual_valorizacao):
        """Simula a valorização do ativo baseado no percentual fornecido"""
        # Convertendo percentual para Decimal para evitar erro de multiplicação entre tipos diferentes
        percentual_valorizacao_decimal = Decimal(percentual_valorizacao)  
        novo_preco = self.preco * (1 + percentual_valorizacao_decimal / 100)
        return novo_preco


class Transacao(models.Model):
    """Registra as transações de compra e venda de ativos"""
    TIPO_CHOICES = [
        ('compra', 'Compra'),
        ('venda', 'Venda'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ativo = models.ForeignKey(Ativo, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # Added default value
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo.capitalize()} - {self.ativo.nome}"

    def save(self, *args, **kwargs):
        # Calcular o valor total da transação antes de salvar
        self.valor_total = self.quantidade * self.preco_unitario if self.valor_total == 0 else self.valor_total
        super().save(*args, **kwargs)


class Portfolio(models.Model):
    """Representa o portfólio do usuário"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ativo = models.ForeignKey(Ativo, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    valor_total = models.DecimalField(max_digits=15, decimal_places=2,)

    def __str__(self):
        return f"{self.usuario.username} - {self.ativo.nome}"

    def atualizar_valor_total(self):
        """Atualiza o valor total do ativo no portfólio"""
        # Aqui também podemos garantir que estamos multiplicando Decimal por Decimal
        self.valor_total = self.quantidade * self.ativo.preco
        self.save()


class Saldo(models.Model):
    """Armazena o saldo disponível do usuário"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    saldo_disponivel = models.DecimalField(max_digits=15, decimal_places=2, default=100000)

    def __str__(self):
        return f"Saldo de {self.usuario.username}: R$ {self.saldo_disponivel}"

    def atualizar_saldo(self, valor):
        """Atualiza o saldo disponível"""
        # Garantindo que o valor a ser adicionado seja do tipo Decimal
        self.saldo_disponivel += Decimal(valor)
        self.save()

