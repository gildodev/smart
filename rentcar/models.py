
import math
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models import Func, FloatField



class Marca(models.Model):
    marca = models.CharField(max_length=500, verbose_name='Nome da marca', unique=True)
    imagem_marca = models.ImageField(upload_to='imagem_marca/', verbose_name='Imagem da Marca', blank=True)
    
    class Meta:
        verbose_name = 'Marca de Veículo'
        verbose_name_plural = 'Marcas dos Veículos'
        ordering = ['-pk']


    def __str__(self):
        return self.marca



class Slides(models.Model):
    titulo = models.CharField(max_length=200, verbose_name='titulo',null=True)
    subtitulo = models.CharField(max_length=500, verbose_name='Subtitulo', null=True)
    descricao = models.TextField(max_length=500, verbose_name='Descricao',null=True)
    imagem_slide = models.ImageField(upload_to='imagem_slide/', verbose_name='Imagem', blank=True)
    mostrar_tudo=models.BooleanField(default=True)
    apenas_imagem=models.BooleanField()
    apenas_texto=models.BooleanField()

    class Meta:
        verbose_name = 'Slide'
        verbose_name_plural = 'Slides'
        ordering = ['-pk']

    def __str__(self):
        return self.titulo
    

class Categoria(models.Model):
    categoria = models.CharField(max_length=500, verbose_name='Nome da Categoria', unique=True)
    imagem_categoria = models.ImageField(upload_to='imagem_categoria/', verbose_name='Imagem da Categoria', blank=True)
    
    class Meta:
        verbose_name = 'Categoria de Veículos'
        verbose_name_plural = 'Categorias dos Veículos'
        ordering = ['-pk']

    def __str__(self):
        return self.categoria

class PerguntasFrequentes(models.Model):
    questao = models.CharField(max_length=1000, unique=True)
    resposta = models.TextField()
    
    class Meta:
        verbose_name = 'Pergunta Frequente'
        verbose_name_plural = 'Perguntas Frequentes'
        ordering = ['-pk']
    
    def __str__(self):
        return self.questao


class Veiculo(models.Model):
    COMBUSTIVEL = [
        ('Gasolina', 'Gasolina'),
        ('Diesel', 'Diesel'),
        ('Petroleo', 'Petroleo')
    ]

    CONDICAO = [
        ('Km', 'Km'),
        ('Hora', 'Hora'),
        ('Dia', 'Dia'),
        ('Semanal', 'Semanal'),
        ('Mensal', 'Mensal'),
        ('Anual', 'Anual'),
    ]

    TRANSMISSAO = [
        ('Automático', 'Automático'),
        ('Manual', 'Manual'),
    ]

    proprietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proprietario_veiculo')
    modelo = models.CharField(max_length=200,)
    descricao = models.TextField(blank=True, null=True)
    placa = models.CharField(max_length=500, unique=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, related_name='categoria_veiculos')
    marca = models.ForeignKey('Marca', on_delete=models.CASCADE, related_name='marca_veiculos')
    ano = models.IntegerField(blank=True)
    tempo_condicao = models.IntegerField(default=1)
    numero_portas = models.IntegerField()
    numero_pessoas = models.IntegerField()
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text='Ex: 1000.00', error_messages={'invalid': 'Erro ao introduzir o valor'})
    ultimo_preco = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0.00,)
    condicao_aplicada = models.CharField(max_length=200, choices=CONDICAO)
    combustivel = models.CharField(max_length=200, choices=COMBUSTIVEL)
    transmissao = models.CharField(max_length=200, choices=TRANSMISSAO)
    imagem_veiculo = models.ImageField(blank=True, upload_to='imagens_veiculos/',)
    localizacao = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=2, default=1.5,)
    longitude = models.DecimalField(max_digits=10, decimal_places=2, default=1.5,)
    distancia_entrega = models.DecimalField(max_digits=10, decimal_places=2, default=1.5,)
    distancia_devolucao = models.DecimalField(max_digits=10, decimal_places=2, default=1.5,)
    com_motorista = models.BooleanField()
    disponivel = models.BooleanField(default=True)
    ac = models.BooleanField()
    gps = models.BooleanField()
    preco_baixou = models.BooleanField(default=False)
    musica = models.BooleanField()
    bluetooth = models.BooleanField()
    url = models.SlugField(editable=False)
    num_requisicoes = models.PositiveBigIntegerField(null=True, editable=False)
    num_pedidos = models.PositiveBigIntegerField(null=True, editable=False)
    data_adicionado = models.DateField(auto_now=True)

    class Meta:
        ordering = ('-num_pedidos',)

    def __str__(self):
        return self.modelo

    def getCount(self):
        return self.objects.count()
    
    def getLat(self):
        lat=str(self.latitude).replace(',','.')
        return lat

    def getLng(self):
        lng=str(self.longitude).replace(',','.')
        return lng

    def save(self, *args, **kwargs):
        antipreco = Veiculo.objects.filter(pk=self.pk).first()
        if antipreco:
            if self.ultimo_preco < self.preco:
                self.ultimo_preco = antipreco.preco
        else:
            if self.ultimo_preco < self.preco:
                self.ultimo_preco = self.preco

        self.url = slugify(self.placa)
        super(Veiculo, self).save(*args, **kwargs)

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Raio da Terra em km
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def distancia_entre_pontos(self, lat1, lon1, lat2, lon2):
        print(f'Distancia: {self.haversine(lat1, lon1, lat2, lon2)}')
        return self.haversine(lat1, lon1, lat2, lon2)

    def verifica_distancias(self, lat_entrega, lon_entrega, lat_devolucao, lon_devolucao):
        distancia_calculada_entrega = self.distancia_entre_pontos(lat_entrega, lon_entrega, self.latitude, self.longitude)
        distancia_calculada_devolucao = self.distancia_entre_pontos(lat_devolucao, lon_devolucao, self.latitude, self.longitude)
        return (distancia_calculada_entrega <= self.distancia_entrega and 
                distancia_calculada_devolucao <= self.distancia_devolucao)


class TermosCondicoes(models.Model):
    veiculo=models.ForeignKey(Veiculo, on_delete=models.CASCADE,related_name='termos')
    titulo=models.CharField(max_length=250, unique=True)
    descricao=models.TextField()
    data_adicionado=models.DateField(auto_now=True)


    def __str__(self):
        return self.titulo
    

    
class Galeria(models.Model):
    veiculo=models.ForeignKey(Veiculo, on_delete=models.CASCADE,related_name='galeria')
    imagem_galeria=models.ImageField(blank=True, upload_to='imagens_veiculos/', )

    def __str__(self):
        return self.veiculo.modelo
    

# Request
class Request(models.Model):
    STATUS=[
        ('Processando','Processando'),
        ('Pendente','Pendente'),
        ('Reprovado','Reprovado'),
        ('Aprovado','Aprovado'),
        ('Negociação','Negociação'),
        ('Cancelado','Cancelado'),
    ]

    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='request')
    local_entrega = models.CharField(max_length=255)
    coordenadas_entregas = models.CharField(max_length=255, blank=True)
    local_devolucao = models.CharField(max_length=255)
    coordenadas_devolucao = models.CharField(max_length=255, blank=True)
    data_entrega = models.DateField()
    hora_entrega = models.TimeField()
    data_devolucao = models.DateField()
    hora_devolucao = models.TimeField()
    status=models.CharField(max_length=200, choices=STATUS, default='Processando')
    data_adicionado=models.DateField(auto_now=True)

    def __str__(self):
        return self.status

class Pedido(models.Model):

    STATUS=[
        ('Pendente','Pendente'),
        ('Reprovado','Reprovado'),
        ('Aprovado','Aprovado'),
        ('Negociação','Negociação'),
        ('Cancelado','Cancelado'),
    ]

    veiculo=models.ForeignKey(Veiculo, on_delete=models.CASCADE,related_name='pedido_veiculo')
    dono=models.ForeignKey(User, on_delete=models.CASCADE,related_name='pedido_dono')
    cliente=models.ForeignKey(User, on_delete=models.CASCADE,related_name='pedido_cliente')
    local_entrega=models.CharField(max_length=550)
    motivo_cancelamento=models.CharField(max_length=550, null=True)
    local_devolucao=models.CharField(max_length=550)
    duracao=models.CharField(max_length=250, null=True)
    distancia=models.CharField(max_length=250,null=True)
    status=models.CharField(max_length=250, choices=STATUS, default='Pendente')
    lida=models.BooleanField(default=False)
    data_entrega=models.DateTimeField()
    data_devolucao=models.DateTimeField()
    observacao_cliente=models.TextField(null=True)
    observacao_dono=models.TextField(null=True)
    data_submitido=models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-pk',)

    def preco_estimativa(self):
        return f'{self.veiculo.preco * self.veiculo.tempo_condicao * int(self.duracao)}'

    def __str__(self):
        return self.veiculo.modelo


class Booking(models.Model):

    STATUS=[
        ('Andamento','Andamento'),
        ('Completo','Completo'),
        ('Aprovado','Aprovado'),
        ('Cancelado','Cancelado'),
    ]

    veiculo=models.ForeignKey(Veiculo, on_delete=models.CASCADE,related_name='booking_veiculo')
    dono=models.ForeignKey(User, on_delete=models.CASCADE,related_name='booking_dono')
    cliente=models.ForeignKey(User, on_delete=models.CASCADE,related_name='booking_cleinte')
    duracao=models.CharField(max_length=250, default='1 dia')
    status=models.CharField(max_length=250, choices=STATUS, default='Andamento')
    data_inicio=models.DateField()
    data_fim=models.DateField()
    observacao_cliente=models.TextField()
    observacao_dono=models.TextField()
    data_submitido=models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-pk',)

    def __str__(self):
        return self.veiculo.modelo



class Notificacao(models.Model):
    STATUS=[
        ('Pedido','Pedido'),
        ('Booking','Booking'),
    ]

    titulo=models.CharField(max_length=1000)
    user=models.ForeignKey(User, on_delete=models.CASCADE,related_name='notificacao')
    lida=models.BooleanField(default=False)
    data_modificado=models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-pk',)

    def __str__(self):
        return self.titulo

