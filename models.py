from django.db import models
from django.contrib.auth.models import User
from rentcar.models import *
import re


class Configuracoes(models.Model):
    nome_site = models.CharField(max_length=100, verbose_name='Nome do Site')
    slogan_principal = models.CharField( default='Conectando Empresas, Movendo Cargas',max_length=100, verbose_name='Slogan da empresa', blank=True)
    descricao_principal = models.TextField(verbose_name='Descrição do Site')
    logotipo = models.ImageField(upload_to='logotipo/', verbose_name='Logotipo_principal', blank=True)
    
    nome_site_delivery = models.CharField(max_length=100, verbose_name='Nome do Site de Delivery', blank=True)
    nome_site_rentcar = models.CharField(max_length=100, verbose_name='Nome do Site de Rent Car', blank=True)
    nome_site_taxi = models.CharField(max_length=100, verbose_name='Nome do Site de taxi', blank=True)
    slogan = models.CharField( default='Conectando Empresas, Movendo Cargas',max_length=100, verbose_name='Slogan do serviço de delivery', blank=True)
    slogan = models.CharField( default='Conectando Empresas, Movendo Cargas',max_length=100, verbose_name='Slogan do serviço de rentcar', blank=True)
    slogan = models.CharField( default='Conectando Empresas, Movendo Cargas',max_length=100, verbose_name='Slogan do serviço de taxi', blank=True)

    logo_delivery = models.ImageField(upload_to='logotipo/', verbose_name='Logotipo_delivery', blank=True)
    logo_rentcar = models.ImageField(upload_to='logotipo/', verbose_name='Logotipo_rentcar', blank=True)
    logo_taxi = models.ImageField(upload_to='logotipo/', verbose_name='Logotipo_taxi', blank=True)

    descricao_delivery = models.TextField(verbose_name='Descrição do Site de Delivery', blank=True)
    descricao_rentcar = models.TextField(verbose_name='Descrição do Site de Rent Car', blank=True)
    descricao_taxi = models.TextField(verbose_name='Descrição do Site  de Taxi', blank=True)
    email = models.EmailField(verbose_name='E-mail de Contato')

    
    phone = models.CharField(max_length=20, verbose_name='Telefone')
    url=models.URLField(max_length=50, verbose_name='Url da plataforma', null=True, blank=True)


    class Meta:
        verbose_name = 'Configuração do Site'
        verbose_name_plural = 'Configurações do Site'

    def __str__(self):
        return self.nome_site


class Servicos(models.Model):
    SERVICE=[
        ('Rentcar', 'Rentcar'),
        ('Taxi', 'Taxi'),
        ('Delivery', 'Delivery')
    ]
    servico=models.CharField(max_length=505, choices=SERVICE)
    imagem_servico=models.ImageField(blank=True, upload_to='servicos/', )
    descricao=models.TextField(null=True,blank=True)
    data_modificado=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.servico


class Profissional(models.Model):
    servico=models.ForeignKey(Servicos, on_delete=models.CASCADE, related_name='servico_prestado')
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='profissional')
    foto_perfil=models.ImageField(blank=True, upload_to='users_profissional/', )
    telefone = models.CharField(max_length=15)
    sobre=models.TextField(max_length=1000,default='')
    localizacao=models.CharField(max_length=300,default='')
    credito=models.IntegerField( null=True)
    data_modificado=models.DateTimeField(auto_now=True)

class Proprietario(models.Model):
    servico=models.ForeignKey(Servicos, on_delete=models.CASCADE, related_name='servico_rentcar')
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='proprietario')
    foto_perfil=models.ImageField(blank=True, upload_to='users_proprietarios/', )
    telefone = models.CharField(max_length=15)
    whatsapp = models.CharField(max_length=15)
    sobre=models.TextField(max_length=1000,default='')
    localizacao=models.CharField(max_length=300,default='')
    credito=models.IntegerField( null=True)
    data_modificado=models.DateTimeField(auto_now=True)

    def validar_telefone_mz(numero):
        # Prefixos por operador
        prefixos_operadores = {
            'Vodacom': ['84', '85'],
            'Movitel': ['86', '87'],
            'TMCEL': ['82','83'],
        }

        numero = re.sub(r'\D', '', numero)

        # Verifica se o número começa com 258 ou 8 (indicando Moçambique)
        if numero.startswith('258'):
            numero = numero[3:]  # Remove o código do país
        elif numero.startswith('8'):
            pass  # Número já está no formato local
        else:
            return False, "Número inválido para Moçambique"

        # Verifica se o número tem exatamente 9 dígitos
        if len(numero) != 9:
            return False, "Número deve ter 9 dígitos"

        # Identifica o operador
        prefixo = numero[:2]  # Considera os dois primeiros dígitos como prefixo
        for operador, prefixos in prefixos_operadores.items():
            if prefixo in prefixos:
                return True, operador

        return False, "Prefixo não reconhecido para qualquer operador"


    def __str__(self):
        return self.user.get_full_name()


class Taxi(models.Model):
    servico=models.ForeignKey(Servicos, on_delete=models.CASCADE, related_name='servico_taxi')
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='taxi')
    foto_perfil=models.ImageField(blank=True, upload_to='users_taxi/', )
    telefone = models.CharField(max_length=15)
    whatsapp = models.CharField(max_length=15)
    sobre=models.TextField(max_length=1000,default='')
    localizacao=models.CharField(max_length=300,default='')
    credito=models.IntegerField( null=True)
    data_modificado=models.DateTimeField(auto_now=True)

    def validar_telefone_mz(numero):
        # Prefixos por operador
        prefixos_operadores = {
            'Vodacom': ['84', '85'],
            'Movitel': ['86', '87'],
            'TMCEL': ['82','83'],
        }

        numero = re.sub(r'\D', '', numero)

        # Verifica se o número começa com 258 ou 8 (indicando Moçambique)
        if numero.startswith('258'):
            numero = numero[3:]  # Remove o código do país
        elif numero.startswith('8'):
            pass  # Número já está no formato local
        else:
            return False, "Número inválido para Moçambique"

        # Verifica se o número tem exatamente 9 dígitos
        if len(numero) != 9:
            return False, "Número deve ter 9 dígitos"

        # Identifica o operador
        prefixo = numero[:2]  # Considera os dois primeiros dígitos como prefixo
        for operador, prefixos in prefixos_operadores.items():
            if prefixo in prefixos:
                return True, operador

        return False, "Prefixo não reconhecido para qualquer operador"



    def __str__(self):
        return self.user.get_full_name()
    


class Delivery(models.Model):
    servico=models.ForeignKey(Servicos, on_delete=models.CASCADE, related_name='servico_delivery')
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='delivery')
    foto_perfil=models.ImageField(blank=True, upload_to='users_delivery/', )
    telefone = models.CharField(max_length=15)
    whatsapp = models.CharField(max_length=15)
    sobre=models.TextField(max_length=1000,default='')
    localizacao=models.CharField(max_length=300,default='')
    credito=models.IntegerField( null=True)
    data_modificado=models.DateTimeField(auto_now=True)


    def validar_telefone_mz(numero):
        # Prefixos por operador
        prefixos_operadores = {
            'Vodacom': ['84', '85'],
            'Movitel': ['86', '87'],
            'TMCEL': ['82','83'],
        }

        numero = re.sub(r'\D', '', numero)

        # Verifica se o número começa com 258 ou 8 (indicando Moçambique)
        if numero.startswith('258'):
            numero = numero[3:]  # Remove o código do país
        elif numero.startswith('8'):
            pass  # Número já está no formato local
        else:
            return False, "Número inválido para Moçambique"

        # Verifica se o número tem exatamente 9 dígitos
        if len(numero) != 9:
            return False, "Número deve ter 9 dígitos"

        # Identifica o operador
        prefixo = numero[:2]  # Considera os dois primeiros dígitos como prefixo
        for operador, prefixos in prefixos_operadores.items():
            if prefixo in prefixos:
                return True, operador

        return False, "Prefixo não reconhecido para qualquer operador"



    def __str__(self):
        return self.user.get_full_name()



class Motorista(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE,related_name='motorista')
    nome = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    foto_perfil=models.ImageField(blank=True, upload_to='users_motoristas/', )
    copia_carta=models.ImageField(blank=True, upload_to='users_motoristas_copia_carta/', )
    telefone = models.CharField(max_length=15)
    nuit = models.CharField(max_length=15, null=True)
    ano_exp = models.IntegerField(null=True)
    carta_conducao=models.CharField(max_length=200, unique=True)
    localizacao=models.CharField(max_length=300)
    credito=models.IntegerField( null=True)
    data_modificado=models.DateField(auto_now=True)

    def __str__(self):
        return self.user.get_full_name()
    
    def validar_telefone_mz(numero):
        # Prefixos por operador
        prefixos_operadores = {
            'Vodacom': ['84', '85'],
            'Movitel': ['86', '87'],
            'TMCEL': ['82','83'],
        }

        numero = re.sub(r'\D', '', numero)

        # Verifica se o número começa com 258 ou 8 (indicando Moçambique)
        if numero.startswith('258'):
            numero = numero[3:]  # Remove o código do país
        elif numero.startswith('8'):
            pass  # Número já está no formato local
        else:
            return False, "Número inválido para Moçambique"

        # Verifica se o número tem exatamente 9 dígitos
        if len(numero) != 9:
            return False, "Número deve ter 9 dígitos"

        # Identifica o operador
        prefixo = numero[:2]  # Considera os dois primeiros dígitos como prefixo
        for operador, prefixos in prefixos_operadores.items():
            if prefixo in prefixos:
                return True, operador

        return False, "Prefixo não reconhecido para qualquer operador"

    

class Cliente(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')
    foto_perfil=models.ImageField(blank=True, upload_to='users_clientes/', )
    telefone = models.CharField(max_length=15)
    outro_nome = models.CharField(max_length=505)
    outro_telefone = models.CharField(max_length=505)
    sobre=models.TextField(max_length=1000,default='')
    localizacao=models.CharField(max_length=300,default='')
    data_modificado=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.get_full_name()
    @staticmethod
    def validar_telefone_mz(numero):
        # Prefixos por operador
        prefixos_operadores = {
            'Vodacom': ['84', '85'],
            'Movitel': ['86', '87'],
            'TMCEL': ['82','83'],
        }

        numero = re.sub(r'\D', '', numero)

        # Verifica se o número começa com 258 ou 8 (indicando Moçambique)
        if numero.startswith('258'):
            numero = numero[3:]  # Remove o código do país
        elif numero.startswith('8'):
            pass  # Número já está no formato local
        else:
            return False, "Número inválido para Moçambique"

        # Verifica se o número tem exatamente 9 dígitos
        if len(numero) != 9:
            return False, "Número deve ter 9 dígitos"

        # Identifica o operador
        prefixo = numero[:2]  # Considera os dois primeiros dígitos como prefixo
        for operador, prefixos in prefixos_operadores.items():
            if prefixo in prefixos:
                return True, operador

        return False, "Prefixo não reconhecido para qualquer operador"


class Notificacoes(models.Model):
    emissor=models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes_emissor')
    receptor=models.OneToOneField(User, on_delete=models.CASCADE, related_name='notificacoes_receptor')
    servico=models.ForeignKey(Servicos, on_delete=models.CASCADE, related_name='servico_notificaoes')
    titulo = models.CharField(max_length=500)
    notificacao_vista=models.BooleanField()
    data_modificado=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

class Historico(models.Model):

    STATUS=[
        ('Completo','Completo'),
        ('Cancelado','Cancelado'),
        ('Negociação','Negociação'),
        ('Pendente','Pendente')
    ]

    cliente=models.ForeignKey(User, on_delete=models.CASCADE, related_name='historico_cliente')
    profissional=models.ForeignKey(User, on_delete=models.CASCADE, related_name='historico_profissional')
    veiculo_rentcar=models.ForeignKey(Veiculo, null=True, on_delete=models.CASCADE, related_name='veiculo_rentcar')
    veiculo_delivery=models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='veiculo_delivery')
    veiculo_taxi=models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='veiculo_taxi')
    servico=models.ForeignKey(Servicos, on_delete=models.CASCADE, related_name='servico_historico')
    pedido = models.ForeignKey(Pedido, null=True, on_delete=models.CASCADE, related_name='pedido_rentcar_historico')
    local1 = models.CharField(max_length=500, null=True)
    local2 = models.CharField(max_length=500, null=True)
    status = models.CharField(max_length=500, choices=STATUS, null=True, default="Pendente")
    data_modificado=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Cliente {self.cliente.get_full_name()} fez pedido ao serviço de {self.servico}.'

    class Meta:
        ordering=['-pk']



    

