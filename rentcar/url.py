from django.urls import path
from .views import *

urlpatterns = [
    path('', Home.index, name='rentcar-home'),
    path('veiculos/', Veiculos.list, name='rentcar-list'),
    path('veiculo/novo/', Veiculos.novo, name='rentcar-novo'),
    path('veiculo/<str:placa>/modificar/', Veiculos.modificar, name='rentcar-modificar'),
    path('veiculo/<str:placa>/remover/', Veiculos.remover, name='rentcar-remover'),
    # Imagens
    path('galeria/', galeria.list, name='rentcar-galeria'),
    path('galeria/nova/', galeria.novo, name='rentcar-galeria-nova'),
    path('galeria/<int:pk>/modificar/', galeria.modificar, name='rentcar-galeria-modificar'),
    path('galeria/<int:pk>/remover/', galeria.remover, name='rentcar-galeria-remover'),
    # Normas
    path('normas/', termoscondicoes.list, name='rentcar-normas'),
    path('normas/nova/', termoscondicoes.novo, name='rentcar-normas-nova'),
    path('normas/<int:pk>/modificar/', termoscondicoes.modificar, name='rentcar-normas-modificar'),
    path('normas/<int:pk>/remover/', termoscondicoes.remover, name='rentcar-normas-remover'),

    # Motorista
    path('motorista/', Motoristas.list, name='rentcar-motorista'),
    path('motorista/novo/', Motoristas.novo, name='rentcar-motorista-novo'),
    path('motorista/<str:carta>/modificar/', Motoristas.modificar, name='rentcar-motorista-modificar'),
    path('motorista/<str:carta>/remover/', Motoristas.remover, name='rentcar-motorista-remover'),

    # Cliente
    path('veiculo/ver-em-grid/', Veiculos.listgrid, name='rentcar-list-grid'),
    path('dashboard/', Cliente.dashboard, name='rentcar-dashboard'),
    path('dashboard/minha-conta/', Cliente.minhaconta, name='rentcar-dashboard-minha-conta'),
    path('dashboard/minha-conta-change/', Cliente.changeminhaconta, name='rentcar-dashboard-minha-conta-change'),
    path('dashboard/minha-conta-delete/', Cliente.deleteminhaconta, name='rentcar-dashboard-minha-conta-delete'),
    path('dashboard/minha-conta-update/', Cliente.modificarminhaconta, name='rentcar-dashboard-minha-conta-post'),
    path('veiculo/ver-em-lista/', Veiculos.listalista, name='rentcar-list-lista'),
    path('veiculo/<slug:placa>/', Veiculos.detalhesVeiculo, name='rentcar-detalhe-veiculo'),

    # Cliente Requests
    path('request/', request.request, name='rentcar-request'),
    path('reserva/<slug:placa>', request.reserva, name='rentcar-reserva'),
    path('historico/<int:pk>/', request.historico, name='rentcar-historico'),
    path('historico/<int:pk>/cancelar/', request.historicoCancelar, name='rentcar-historico-cancelar'),
    

    # Meus Bookings
    path('booking/', booking.booking, name='rentcar-bookings'),
    path('pedidos/', booking.pedidos, name='rentcar-pedidos'),
    path('pedido-update/<int:pk>/', booking.update, name='rentcar-pedido-update'),
    path('booking/<slug:placa>/confirmar/', booking.confirmar, name='rentcar-booking-confirmar'),
    
    # Notificações
    path('notificacao-delete/', notificacao.delete, name='rentcar-notificacao-detele'),


    # Proprietario
    path('minha-conta/', proprietario.minhaconta, name='rentcar-dashboard-minha-conta'),
    path('minha-conta-change/', proprietario.changeminhaconta, name='rentcar-dashboard-minha-conta-change'),
    path('minha-conta-delete/', proprietario.deleteminhaconta, name='rentcar-dashboard-minha-conta-delete'),
    path('minha-conta-update/', proprietario.modificarminhaconta, name='rentcar-dashboard-minha-conta-post'),
    
]
