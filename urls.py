from django.urls import path
from .views import *

urlpatterns = [
    path('', index.index, name='smart'),
    path('login/', auth.Login, name='smart-login'),
    path('cadastro/', auth.cadastro, name='smart-cadastro'),
    path('cadastro-cliente/', auth.cliente, name='smart-cadastro-proc-servicos'),
    path('cadastro-profissional/', auth.profissional, name='smart-cadastro-prest-servicos'),
    path('sair/', auth.Logout, name='smart-sair'),
    path('api/login/', auth.login_view, name='smart-login-api'),
    path('api/cadastro-cliente/', auth.clienteAPI, name='smart-cadastro-proc-servicos-api'),
    path('api/cadastro-profissional/', auth.ProfissionalAPI, name='smart-cadastro-prest-servicos-api'),
    path("api/", api.urls),
]
