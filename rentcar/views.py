from math import radians
from django.shortcuts import redirect, render, HttpResponse, get_list_or_404,get_object_or_404
from django.contrib import messages
from config.models import *
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.auth.models import User
from datetime import datetime, date , time
from django.db.models import Q, Count
from django.urls import reverse
from asgiref.sync import async_to_sync
from django.utils.dateformat import format
from django.utils import timezone
from django.http import JsonResponse


# Home
class Home:
    def index(request):
        conf=Configuracoes.objects.first()
        categoria=Categoria.objects.all()
        categorias=[]
        for marca in categoria:
            if marca.categoria_veiculos.all():
                categorias.append(marca)

        # Agrega contagens de pedidos e reservas em uma única consulta
        status_counts = Pedido.objects.filter(dono=request.user).values('status').annotate(count=Count('pk')).order_by('status')
        booking_status_counts = Booking.objects.filter(dono=request.user).values('status').annotate(count=Count('pk')).order_by('status')

        pedidos_hoje= Pedido.objects.filter(dono=request.user).values('status').annotate(count=Count('pk')).order_by('status')[:5]
        
        # Dicionários para fácil acesso
        pedido_counts = {status_count['status']: status_count['count'] for status_count in status_counts}
        booking_counts = {status_count['status']: status_count['count'] for status_count in booking_status_counts}
        
        # Extrai contagens específicas ou define como 0 se não existirem
        total_pd_pendente = pedido_counts.get('Pendente', 0)
        total_pd_cancelado = pedido_counts.get('cancelado', 0)
        total_bk_completo = booking_counts.get('Completo', 0)
        total_bk_andamento = booking_counts.get('Andamento', 0)  

        # Obter a data atual
        now = timezone.now()

        # Filtrar pedidos pendentes de hoje
        pedidos_hoje_pendentes = Pedido.objects.filter(
            dono=request.user,
            status='Pendente',
        ).annotate(count=Count('pk')).order_by('status')[:5]

        if request.user.is_authenticated and hasattr(request.user,'proprietario'):

            return render(request, 'rentcar/profissional/index.html',{
                'config':conf,
                'total_pd_pendente':total_pd_pendente,
                'total_pd_cancelado':total_pd_cancelado,
                'total_bk_completo':total_bk_completo,
                'total_bk_andamento':total_bk_andamento,
                'pedidos_hoje_pendentes': pedidos_hoje_pendentes,
                'titulo':'Página Inicial',
                'back':'d-none',


            })
        elif request.user.is_authenticated or not request.user.is_authenticated or hasattr(request.user,'cliente'):
            
            slides=Slides.objects.all()
            marca=Marca.objects.all()
            marcas=[]
            for marca in marca:
                if marca.marca_veiculos.all():
                    marcas.append(marca)

            categoria=Categoria.objects.all()
            categorias=[]
            for marca in categoria:
                if marca.categoria_veiculos.all():
                    categorias.append(marca)
            motorista=Veiculo.objects.exclude(com_motorista=False)
            semmotorista=Veiculo.objects.exclude(com_motorista=True)
            pergFreq=PerguntasFrequentes.objects.all()
            active='active'
            veiculo=Veiculo.objects.all()
            ano=veiculo.values('ano').distinct()
            combustivel=veiculo.values('combustivel','pk').distinct()
            condicao=veiculo.values('condicao_aplicada','pk').distinct()
            pessoas=veiculo.values('numero_pessoas').distinct()
            portas=veiculo.values('numero_portas').distinct()
            transmissao=veiculo.values('transmissao').distinct()


            return render(request, 'rentcar/rentcar.html',{
                'config':conf,
                'slides':slides,
                'marcas':marcas,
                'categorias':categorias,
                'motorista':motorista,
                'semmotorista':semmotorista,
                'pergFreq':pergFreq,
                'active':active,
                'ano':ano,
                'combustivel':combustivel,
                'condicao':condicao,
                'pessoas':pessoas,
                'portas':portas,
                'transmissao':transmissao,
                'veiculos':veiculo,
            })
        
        return redirect('smart-login')

class Veiculos:
    # Cadastro
    @login_required(login_url='smart-login')
    def list(request):
        marca=Marca.objects.all()
        categoria=Categoria.objects.all()
        conf=Configuracoes.objects.first()
        veiculo=Veiculo.objects.filter(proprietario=request.user)
        if  hasattr(request.user,'proprietario'):
            return render(request, 'rentcar/profissional/lista_veiculos.html',{
                'config':conf,
                'categoria':categoria,
                'marca':marca,
                'veiculos':veiculo,
                'titulo':'Meus Veículos',
                'veiculo':'active'
            })
        return redirect('smart-login')


    @login_required(login_url='smart-login')
    def novo(request):
        marca=Marca.objects.all()
        categoria=Categoria.objects.all()
        conf=Configuracoes.objects.first()
        if hasattr(request.user,'proprietario'):
            user=User.objects.get(pk=request.user.pk)
            if request.method == 'POST':
                modelo = request.POST.get('modelo')
                placa = request.POST.get('placa')
                categoria_id = request.POST.get('categoria')
                marca_id = request.POST.get('marca')
                ano = request.POST.get('ano')
                numero_portas = request.POST.get('numero_portas')
                numero_pessoas = request.POST.get('numero_pessoas')
                preco = request.POST.get('preco')
                condicao_aplicada = request.POST.get('condicao')
                combustivel = request.POST.get('combustivel')
                transmissao = request.POST.get('transmissao')
                localizacao = request.POST.get('localizacao')
                descricao = request.POST.get('descricao')
                com_motorista = request.POST.get('com_motorista') == 'on'
                musica = request.POST.get('musica') == 'on'
                bluetooht = request.POST.get('bluetooth') == 'on'
                gps = request.POST.get('gps') == 'on'
                ac = request.POST.get('ac') == 'on'
                imagem_veiculo = request.FILES.get('imagem')
                coordenadas = request.POST.get('coordenadas')
                distancia_entrega = str(request.POST.get('distancia_entrega')).replace(',','.')
                distancia_devolucao = str(request.POST.get('distancia_devolucao')).replace(',','.')
                latitude=float(str(coordenadas).split(',')[0])
                longitude=float(str(coordenadas).split(',')[1])
                
                
                try:
                    categoria = Categoria.objects.get(id=categoria_id)
                    marca = Marca.objects.get(id=marca_id)
                except Categoria.DoesNotExist or Marca.DoesNotExist:
                    return JsonResponse({'success':False,'message':'Categoria ou Marca inválida.'}, status=401)

                veiculo = Veiculo(
                    distancia_entrega=distancia_entrega,
                    distancia_devolucao=distancia_devolucao,
                    longitude=longitude,
                    latitude=latitude,
                    modelo=modelo,
                    placa=placa,
                    categoria=categoria,
                    marca=marca,
                    ano=ano,
                    numero_portas=numero_portas,
                    numero_pessoas=numero_pessoas,
                    preco=float(preco),
                    condicao_aplicada=condicao_aplicada,
                    combustivel=combustivel,
                    transmissao=transmissao,
                    localizacao=localizacao,
                    com_motorista=com_motorista,
                    proprietario=user,
                    imagem_veiculo=imagem_veiculo,
                    gps=gps,
                    ac=ac,
                    musica=musica,
                    bluetooth=bluetooht,
                    descricao=descricao,
                )
                veiculo.save()
                return JsonResponse({'success':True,'message':'Veículo adicionado com sucesso.'})

            return JsonResponse({'success':False,'message':'Não existe.'}, status=401)
        return JsonResponse({'success':False,'message':'Não tem permissão.'}, status=401)


    @login_required(login_url='smart-login')
    def modificar(request,placa):
        marca=Marca.objects.all()
        categoria=Categoria.objects.all()
        conf=Configuracoes.objects.first()
        veiculo=get_object_or_404(Veiculo, url=placa)
        if hasattr(request.user,'proprietario'):
            if request.method == 'POST':
                modelo = request.POST.get('modelo')
                placa = request.POST.get('placa')
                categoria_id = request.POST.get('categoria')
                marca_id = request.POST.get('marca')
                ano = request.POST.get('ano')
                numero_portas = request.POST.get('numero_portas')
                numero_pessoas = request.POST.get('numero_pessoas')
                preco = request.POST.get('preco')
                condicao_aplicada = request.POST.get('condicao')
                combustivel = request.POST.get('combustivel')
                transmissao = request.POST.get('transmissao')
                localizacao = request.POST.get('localizacao')
                com_motorista = request.POST.get('com_motorista') == 'on'
                imagem_veiculo = request.FILES.get('imagem')
                musica = request.POST.get('musica') == 'on'
                bluetooht = request.POST.get('bluetooth') == 'on'
                gps = request.POST.get('gps') == 'on'
                ac = request.POST.get('ac') == 'on'
                descricao = request.POST.get('descricao')
                coordenadas = request.POST.get('coordenadas')
                distancia_entrega = str(request.POST.get('distancia_entrega')).replace(',','.')
                distancia_devolucao = str(request.POST.get('distancia_devolucao')).replace(',','.')
                print(f'Imagem: {imagem_veiculo}')

                if coordenadas:
                    latitude=float(str(coordenadas).split(',')[0])
                    longitude=float(str(coordenadas).split(',')[1])
                    veiculo.latitude=latitude
                    veiculo.longitude=longitude

                try:
                    categoria = Categoria.objects.get(id=categoria_id)
                    marca = Marca.objects.get(id=marca_id)
                except Categoria.DoesNotExist or Marca.DoesNotExist:
                    return JsonResponse({'success':False,'message':'Categoria ou Marca inválida.'}, status=401)
                
                preco= float(str(preco).replace(',','.'))
                veiculo.distancia_entrega=distancia_entrega
                veiculo.distancia_devolucao=distancia_devolucao
                veiculo.modelo=modelo
                veiculo.placa=placa
                veiculo.categoria=categoria
                veiculo.marca=marca
                veiculo.ano=ano
                veiculo.numero_portas=numero_portas
                veiculo.numero_pessoas=numero_pessoas
                veiculo.preco=preco
                veiculo.condicao_aplicada=condicao_aplicada
                veiculo.combustivel=combustivel
                veiculo.transmissao=transmissao
                veiculo.localizacao=localizacao
                veiculo.com_motorista=com_motorista
                veiculo.gps=gps
                veiculo.ac=ac
                veiculo.musica=musica
                veiculo.bluetooth=bluetooht
                veiculo.descricao=descricao
                if imagem_veiculo:
                    veiculo.imagem_veiculo=imagem_veiculo
                    print(f'Imagem: {imagem_veiculo}')
                
                veiculo.save()
                return JsonResponse({'success':True,'message':'Veículo actualizado com sucesso com sucesso.'}, status=201)

        
            return JsonResponse({'success':False,'message': f'Não existe.{request.method}'}, status=401)

        return JsonResponse({'success':False,'message':'Não tem permissão.'}, status=401)
    

    @login_required(login_url='smart-login')
    def remover(request,placa):
        veiculo=get_object_or_404(Veiculo, placa=placa)
        
        if hasattr(request.user,'proprietario'):
            v=veiculo.modelo
            veiculo.delete()
            return JsonResponse({'success':True,'message':f'{v} removido com sucesso.'})
            
        return redirect('smart-login')
    

    @login_required(login_url='smart-login')
    def get(request,placa):
        veiculo=get_object_or_404(Veiculo, placa=placa)
        categorias=Categoria.objects.all()
        categoria=[{'categoria':categoria.categoria,'pk':categoria.pk} for categoria in categorias]
        marcas=Marca.objects.all()
        marca=[{'marca':marca.marca,'pk':marca.pk}  for marca in marcas]
        veiculo_data=[]
        if hasattr(request.user,'proprietario'):
            veiculo_data.append({
                'placa': veiculo.placa,
                'marca': veiculo.marca.pk,
                'modelo': veiculo.modelo,
                'ano': veiculo.ano,
                'categoria': veiculo.categoria.pk,
                'preco': veiculo.preco,
                'condicao': veiculo.condicao_aplicada,
                'descricao':veiculo.descricao,
                'tempo_condicao':veiculo.tempo_condicao,
                'numero_pessoas':veiculo.numero_pessoas,
                'numero_portas':veiculo.numero_portas,
                'transmissao': veiculo.transmissao,
                'combustivel': veiculo.combustivel,
                'localizacao': veiculo.localizacao,
                'distancia_entrega': veiculo.distancia_entrega,
                'distancia_devolucao': veiculo.distancia_devolucao,
                'motorista': veiculo.com_motorista,
                'ac': veiculo.ac,
                'gps': veiculo.gps,
                'musica': veiculo.musica,
                'bluetooth': veiculo.bluetooth,
                'disponivel': veiculo.disponivel,
                'latitude':veiculo.latitude,
                'longitude':veiculo.longitude,
                'imagem': veiculo.imagem_veiculo.url if veiculo.imagem_veiculo else None,
                'url': reverse('rentcar-modificar', args=[veiculo.url])

                # Adicione outros campos necessários aqui
            })
            return JsonResponse({'veiculo':veiculo_data,'marcas':marca,'categorias':categoria})
        return redirect('smart-login')

    @login_required(login_url='smart-login')
    def actualizar(request):
        veiculo=Veiculo.objects.filter(proprietario=request.user).order_by('-pk')
        
        veiculo_data=[]
        if hasattr(request.user,'proprietario'):
            for veiculo in veiculo:
                veiculo_data.append({
                'placa': veiculo.placa,
                'marca': veiculo.marca.marca,
                'modelo': veiculo.modelo,
                'ano': veiculo.ano,
                'preco': veiculo.preco,
                'condicao': veiculo.condicao_aplicada,
                'pessoas':veiculo.numero_pessoas,
                'portas':veiculo.numero_portas,
                'imagem': veiculo.imagem_veiculo.url if veiculo.imagem_veiculo else None,
                'url': reverse('rentcar-modificar', args=[veiculo.url])

                # Adicione outros campos necessários aqui
            })
            return JsonResponse({'veiculo':veiculo_data})
        return redirect('smart-login')


    # Venda
    @login_required(login_url='smart-login')
    def detalhesVeiculo(request,placa):
        marca=Marca.objects.all()
        categoria=Categoria.objects.all()
        conf=Configuracoes.objects.first()
        veiculo=get_object_or_404(Veiculo, url=placa)
        marcas=[]
        for marca in marca:
            if marca.marca_veiculos.all():
                marcas.append(marca)

        categoria=Categoria.objects.all()
        categorias=[]
        for marca in categoria:
            if marca.categoria_veiculos.all():
                categorias.append(marca)
        
        return render(request, 'rentcar/cliente/lista_detalhes.html',{
            'config':conf,
            'categorias':categorias,
            'marcas':marcas,
            'veiculo':veiculo,
            'v':'active',
        })
    

  
    def listgrid(request):
        conf=Configuracoes.objects.first()
        
        if not request.user.is_authenticated or hasattr(request.user,'cliente'):
            
            slides=Slides.objects.all()
            marca=Marca.objects.all()
            veiculo=Veiculo.objects.all()
            ano=veiculo.values('ano').distinct()
            combustivel=veiculo.values('combustivel','pk').distinct()
            condicao=veiculo.values('condicao_aplicada','pk').distinct()
            pessoas=veiculo.values('numero_pessoas').distinct()
            portas=veiculo.values('numero_portas').distinct()
            transmissao=veiculo.values('transmissao').distinct()

            if request.method == 'GET':
                marc=request.GET.get('marca')
                categ=request.GET.get('categoria')
                an=request.GET.get('ano')
                comb=request.GET.get('combustivel')
                cond=request.GET.get('condicao')
                pessoa=request.GET.get('pessoas')
                porta=request.GET.get('portas')
                trans=request.GET.get('transmissao')
                q=request.GET.get('q')

                if marc or categ or an or comb or cond or pessoa or porta or trans or q:
                    _categ=Categoria.objects.filter(categoria=categ).first()
                    _marca=Marca.objects.filter(marca=marc).first()
                    veiculo=veiculo.filter(
                        Q(categoria= _categ) | Q(marca=_marca) | Q(ano=an)| 
                        Q(combustivel=comb) | Q(numero_pessoas=pessoa) | 
                        Q(numero_portas=porta) |  Q(transmissao=trans) |
                        Q(modelo__icontains=q) | Q(placa__icontains=q) | Q(localizacao=q) |
                        Q(condicao_aplicada=cond)
                    )


            marcas=[]
            for marca in marca:
                if marca.marca_veiculos.all():
                    marcas.append(marca)

            categoria=Categoria.objects.all()
            categorias=[]
            for marca in categoria:
                if marca.categoria_veiculos.all():
                    categorias.append(marca)
            motorista=Veiculo.objects.exclude(com_motorista=False)
            semmotorista=Veiculo.objects.exclude(com_motorista=True)
            return render(request, 'rentcar/cliente/lista_grid.html',{
                'config':conf,
                'slides':slides,
                'marcas':marcas,
                'categorias':categorias,
                'motorista':motorista,
                'semmotorista':semmotorista,
                'veiculo':veiculo,
                'v':'active',
                'ano':ano,
                'condicao':condicao,
                'combustivel':combustivel,
                'pessoas':pessoas,
                'portas':portas,
                'transmissao':transmissao,
            })
        else:
            return redirect(f'smart-login?next=list-grid/')

    def listalista(request):
        conf=Configuracoes.objects.first()
        if not request.user.is_authenticated or hasattr(request.user,'cliente'):
            
            slides=Slides.objects.all()
            marca=Marca.objects.all()
            veiculo=Veiculo.objects.all()
            ano=veiculo.values('ano').distinct()
            combustivel=veiculo.values('combustivel','pk').distinct()
            condicao=veiculo.values('condicao_aplicada','pk').distinct()
            pessoas=veiculo.values('numero_pessoas').distinct()
            portas=veiculo.values('numero_portas').distinct()
            transmissao=veiculo.values('transmissao').distinct()

            if request.method == 'GET':
                marc=request.GET.get('marca')
                categ=request.GET.get('categoria')
                an=request.GET.get('ano')
                comb=request.GET.get('combustivel')
                cond=request.GET.get('condicao')
                pessoa=request.GET.get('pessoas')
                porta=request.GET.get('portas')
                trans=request.GET.get('transmissao')
                q=request.GET.get('q')

                if marc or categ or an or comb or cond or pessoa or porta or trans or q:
                    _categ=Categoria.objects.filter(categoria=categ).first()
                    _marca=Marca.objects.filter(marca=marc).first()
                    veiculo=veiculo.filter(
                        Q(categoria= _categ) | Q(marca=_marca) | Q(ano=an)| 
                        Q(combustivel=comb) | Q(numero_pessoas=pessoa) | 
                        Q(numero_portas=porta) |  Q(transmissao=trans) |
                        Q(modelo__icontains=q) | Q(placa__icontains=q) | Q(localizacao=q) |
                        Q(condicao_aplicada=cond)
                    )


            marcas=[]
            for marca in marca:
                if marca.marca_veiculos.all():
                    marcas.append(marca)

            categoria=Categoria.objects.all()
            categorias=[]
            for marca in categoria:
                if marca.categoria_veiculos.all():
                    categorias.append(marca)
            motorista=Veiculo.objects.exclude(com_motorista=False)
            semmotorista=Veiculo.objects.exclude(com_motorista=True)
            return render(request, 'rentcar/cliente/lista_lista.html',{
                'config':conf,
                'slides':slides,
                'marcas':marcas,
                'categorias':categorias,
                'motorista':motorista,
                'semmotorista':semmotorista,
                'veiculo':veiculo,
                'v':'active',
                'ano':ano,
                'condicao':condicao,
                'combustivel':combustivel,
                'pessoas':pessoas,
                'portas':portas,
                'transmissao':transmissao,
            })
        else:
            return redirect(f'smart-login?next=list-grid/')

class galeria:

    @login_required(login_url='smart-login')
    def list(request):
        marca=Marca.objects.all()
        categoria=Categoria.objects.all()
        conf=Configuracoes.objects.first()
        veiculo=Veiculo.objects.filter(proprietario=request.user)
        if  hasattr(request.user,'proprietario'):
            return render(request, 'rentcar/lista_galeria.html',{
                'config':conf,
                'categorias':categoria,
                'marca':marca,
                'veiculos':veiculo,
                'v':'active',

            })
        return HttpResponse('Não estais autorizado a acessar aqui.')


    @login_required(login_url='smart-login')
    def novo(request):
        conf=Configuracoes.objects.first()
        vl=Veiculo.objects.filter(proprietario=request.user)
        galeria=None
        categorias=Categoria.objects.all()
        categoria=[]
        for marca in categorias:
            if marca.categoria_veiculos.all():
                categoria.append(marca)
        if hasattr(request.user,'proprietario'):
            if request.method == 'POST':
                placa = request.POST.get('veiculo')
                veiculo=Veiculo.objects.get(placa=placa)
                imagem_veiculo = request.FILES.get('imagem')
                galeria=Galeria.objects.create(veiculo=veiculo, imagem_galeria=imagem_veiculo)
                if galeria:
                    messages.success(request, 'Galeria adicionado com sucesso!')
                else:
                    messages.success(request, 'Erro ao criar galeria!')

            return render(request, 'rentcar/nova_galeria.html',{
                'config':conf,
                'veiculos':vl,
                'galeria':galeria,
                'categorias': categoria,
                'v':'active',
            })
        return HttpResponse('Não estais autorizado a acessar aqui.')


    @login_required(login_url='smart-login')
    def modificar(request,pk):
        conf=Configuracoes.objects.first()
        galeria=Galeria.objects.get(pk=pk)
        vl=Veiculo.objects.filter(proprietario=request.user)
        categorias=Categoria.objects.all()
        categoria=[]
        for marca in categorias:
            if marca.categoria_veiculos.all():
                categoria.append(marca)
        if hasattr(request.user,'proprietario'):
            if request.method == 'POST':
                placa = request.POST.get('veiculo')
                veiculo=Veiculo.objects.get(placa=placa)
                imagem_veiculo = request.FILES.get('imagem')
                if galeria:
                    galeria.veiculo=veiculo
                    if imagem_veiculo:
                        galeria.imagem_galeria=imagem_veiculo
                    galeria.save()
                    messages.success(request, 'Galeria alerterado com sucesso!')
                else:
                    messages.success(request, 'Erro ao actualizar galeria!')

            return render(request, 'rentcar/modificar_galeria.html',{
                'config':conf,
                'veiculos':vl,
                'galeria':galeria,
                'categoria':categoria,
                'v':'active',
            })
        return HttpResponse('Não estais autorizado a acessar aqui.')
    

    @login_required(login_url='smart-login')
    def remover(request,pk):
        galeria=get_object_or_404(Galeria, pk=pk)
        
        if hasattr(request.user,'proprietario'):
            
            messages.success(request, f'Imagem da galaria "{galeria}" removido com sucesso.')
            galeria.delete()
            return redirect('rentcar-galeria')
        return HttpResponse('Não estais autorizado a acessar aqui.')
            
class termoscondicoes:

    @login_required(login_url='smart-login')
    def list(request):
        conf=Configuracoes.objects.first()
        veiculo=Veiculo.objects.filter(proprietario=request.user)
        categorias=Categoria.objects.all()
        categoria=[]
        for marca in categorias:
            if marca.categoria_veiculos.all():
                categoria.append(marca)

        if  hasattr(request.user,'proprietario'):
            return render(request, 'rentcar/lista_termos.html',{
                'config':conf,
                'veiculos':veiculo,
                'categorias':categoria,
                'v':'active',
            })
        return HttpResponse('Não estais autorizado a acessar aqui.')


    @login_required(login_url='smart-login')
    def novo(request):
        conf=Configuracoes.objects.first()
        vl=Veiculo.objects.filter(proprietario=request.user)
        normas=None
        if hasattr(request.user,'proprietario'):
            if request.method == 'POST':
                placa = request.POST.get('veiculo')
                titulo = request.POST.get('titulo')
                descricao = request.POST.get('descricao')
                veiculo=Veiculo.objects.get(placa=placa)
                try:
                    normas=TermosCondicoes.objects.create(veiculo=veiculo,titulo=titulo, descricao=descricao)
                
                    if normas:
                        messages.success(request, f'Norma "{normas}" adicionado com sucesso!')
                    else:
                        messages.error(request, 'Erro ao criar uma Norma!')

                except Exception as e:
                    messages.error(request, 'Erro ao criar uma norma, parece que esta norma já foi adicionado.')
            
            return render(request, 'rentcar/novas_normas.html',{
                'config':conf,
                'veiculos':vl,
                'normas':normas,
                'v':'active',
            })
        return HttpResponse('Não estais autorizado a acessar aqui.')


    @login_required(login_url='smart-login')
    def modificar(request,pk):
        conf=Configuracoes.objects.first()
        vl=Veiculo.objects.filter(proprietario=request.user)
        normas=TermosCondicoes.objects.get(pk=pk)
        if hasattr(request.user,'proprietario'):
            if request.method == 'POST':
                placa = request.POST.get('veiculo')
                titulo = request.POST.get('titulo')
                descricao = request.POST.get('descricao')
                veiculo=Veiculo.objects.get(placa=placa)
                try:
                    normas.veiculo=veiculo
                    normas.titulo=titulo
                    normas.descricao=descricao
                    normas.save()
                
                    if normas:
                        messages.success(request, f'Norma "{normas}" actualizado com sucesso!')
                    else:
                        messages.error(request, 'Erro ao actualizar a norma.')

                except Exception as e:
                    messages.error(request, 'Erro ao actualizar a norma, parece que esta norma já foi adicionado.')
            
            return render(request, 'rentcar/modificar_normas.html',{
                'config':conf,
                'veiculos':vl,
                'norma':normas,
                'v':'active',
            })
        return HttpResponse('Não estais autorizado a acessar aqui.')
    

    @login_required(login_url='smart-login')
    def remover(request,pk):
        norma=get_object_or_404(TermosCondicoes, pk=pk)
        
        if hasattr(request.user,'proprietario'):
            
            messages.success(request, f'Norma "{norma}" removido com sucesso.')
            norma.delete()
            return redirect('rentcar-normas')
        return HttpResponse('Não estais autorizado a acessar aqui.')
    
# Motorista
class Motoristas:

    @login_required(login_url='smart-login')
    def list(request):
        conf=Configuracoes.objects.first()
        categorias=Categoria.objects.all()
        categoria=[]
        for marca in categorias:
            if marca.categoria_veiculos.all():
                categoria.append(marca)
        if  hasattr(request.user,'proprietario'):
            return render(request, 'rentcar/lista_motorista.html',{
                'config':conf,
                'categorias':categoria,
                'm':'active',
            })
        return redirect('smart-login')


    @login_required(login_url='smart-login')
    def novo(request):
        conf=Configuracoes.objects.first()
        categorias=Categoria.objects.all()
        categoria=[]
        for marca in categorias:
            if marca.categoria_veiculos.all():
                categoria.append(marca)

        if hasattr(request.user,'proprietario'):
            user=User.objects.get(pk=request.user.pk)
            if request.method == 'POST':
                nome = request.POST.get('nome')
                email = request.POST.get('email')
                carta = request.POST.get('carta')
                nuit = request.POST.get('nuit')
                ano_exp = request.POST.get('ano')
                telefone = request.POST.get('telefone')
                localizacao = request.POST.get('localizacao')
                foto_perfil = request.FILES.get('imagem')
                copia_carta = request.FILES.get('copia')
                
                motorista = Motorista.objects.create(
                    nome=nome,
                    email=email,
                    carta_conducao=carta,
                    telefone=telefone,
                    ano_exp=ano_exp,
                    nuit=nuit,
                    user=user,
                    foto_perfil=foto_perfil,
                    copia_carta=copia_carta,
                    localizacao=localizacao
                )
                if motorista:
                    messages.success(request, f'Motorista "{motorista}" adicionado com sucesso!')
                else:
                    messages.error(request, 'Erro ao adicionar motorista.')
                return redirect('rentcar-motorista')

            return render(request, 'rentcar/novo_motorista.html',{
                'config':conf,
                'categorias':categoria,
                'm':'active',
            })
        return redirect('smart-login')


    @login_required(login_url='smart-login')
    def modificar(request,carta):
        conf=Configuracoes.objects.first()
        motorista=get_object_or_404(Motorista, carta_conducao=carta)
        categorias=Categoria.objects.all()
        categoria=[]
        for marca in categorias:
            if marca.categoria_veiculos.all():
                categoria.append(marca)
        if hasattr(request.user,'proprietario'):
            if request.method == 'POST':
                nome = request.POST.get('nome')
                email = request.POST.get('email')
                carta = request.POST.get('carta')
                nuit = request.POST.get('nuit')
                ano_exp = request.POST.get('ano')
                telefone = request.POST.get('telefone')
                localizacao = request.POST.get('localizacao')
                foto_perfil = request.FILES.get('imagem')
                copia_carta = request.FILES.get('copia')
                
                # Salvar
                motorista.localizacao=localizacao
                motorista.nome=nome,
                motorista.email=email,
                motorista.carta_conducao=carta,
                motorista.telefone=telefone,
                motorista.ano_exp=ano_exp,
                motorista.nuit=nuit,
                motorista.user=request.user,
                motorista.foto_perfil=foto_perfil,

                if copia_carta:
                    motorista.copia_carta=copia_carta
                if foto_perfil:
                    motorista.foto_perfil=foto_perfil
                
                motorista.save()
                messages.success(request, f'Motorista "{motorista}" actualizado com sucesso com sucesso!')

                return redirect('rentcar-motorista-modificar',motorista.carta_conducao )

        
            return render(request, 'rentcar/modificar_motorista.html',{
                'config':conf,
                'motorista':motorista,
                'categorias': categoria,
                'm':'active',
            })
        return redirect('smart-login')
    

    @login_required(login_url='smart-login')
    def remover(request,carta):
        motorista=get_object_or_404(Motorista, carta_conducao=carta)
        
        if hasattr(request.user,'proprietario'):
            
            messages.success(request, f'{motorista} removido com sucesso.')
            motorista.delete()
            return redirect('rentcar-motorista')
        return HttpResponse('Não estais autorizado a acessar aqui.')
            
# Cliente
class Cliente:
    @login_required(login_url='smart-login')
    def dashboard(request):
        conf=Configuracoes.objects.first()
        categorias=Categoria.objects.all()
        categoria=[]
        for marca in categorias:
            if marca.categoria_veiculos.all():
                categoria.append(marca)
        if  hasattr(request.user,'cliente'):
            return render(request, 'rentcar/cliente/dashboard.html',{
                'config':conf,
                'categorias':categoria,
            })
        return redirect('smart-login') 

    @login_required(login_url='smart-login')
    def minhaconta(request):
        conf=Configuracoes.objects.first()
        categorias=Categoria.objects.all()
        categoria=[]

        for marca in categorias:
            if marca.categoria_veiculos.all():
                categoria.append(marca)

        if  hasattr(request.user,'cliente'):

            return render(request, 'rentcar/cliente/minha-conta.html',{
                'config':conf,
                'categorias':categoria,
                'titulo':'Minha Conta'
            })
        return redirect('smart-login')
    
    @login_required(login_url='smart-login')
    def modificarminhaconta(request):
        if  hasattr(request.user,'cliente'):
            first_name=request.POST.get('nome')
            last_name=request.POST.get('sobrenome')
            email=request.POST.get('email')
            telefone=request.POST.get('telefone')
            localizacao=request.POST.get('localizacao')
            foto_perfil=request.FILES.get('imagem')

            tel,erro= request.user.cliente.validar_telefone_mz(telefone)
            if not tel:
                messages.error(request, f"{erro}")
                return redirect('rentcar-dashboard-minha-conta')
            
            print(f'Localizacao: {localizacao}')

            user=request.user
            try:
                user.first_name=str(first_name).title()
                user.last_name=str(last_name).title()
                user.email=email
                user.save()
                if foto_perfil:
                    user.cliente.foto_perfil=foto_perfil
                    
                user.cliente.localizacao=localizacao
                user.cliente.telefone=telefone
                user.cliente.save()

                messages.success(request, f"{first_name} {last_name} Actualizado com sucesso.")
                return redirect('rentcar-dashboard-minha-conta')
            
            except Exception as e:
                messages.error(request, f"Erro ao actualizar o usuario {e}")
                return redirect('rentcar-dashboard-minha-conta')
            
        return redirect('smart-login')


    @login_required(login_url='smart-login')
    def changeminhaconta(request):
        if  hasattr(request.user,'cliente'):
            if request.method == "GET":
                return render(request, 'rentcar/cliente/change_password.html',{
                    'titulo':'Segurança',
                    'config':Configuracoes.objects.first()
                })
            else:
                old_password=request.POST.get('old-passoword')
                username=request.POST.get('username')
                password=request.POST.get('novo-password')

                user=User.objects.get(username=request.user)
                auth=authenticate(request, username=username,password=old_password)
                if auth:
                    user.set_password(password)
                    if password:
                        user.username=username
                    user.save()

                    messages.success(request, f"Passoword actualizado com sucesso.")
                    return redirect('rentcar-dashboard-minha-conta-change')
                else:
                    messages.error(request, f"Dados de acesso inválidos.{auth}")
                    return redirect('rentcar-dashboard-minha-conta-change')
                
        return redirect('smart-login')

    @login_required(login_url='smart-login')
    def deleteminhaconta(request):
        if  hasattr(request.user,'cliente'):
            request.user.delete()
            return redirect('rentcar-home')
        return redirect('smart-login')

# Booking
class booking:
    @login_required(login_url='smart-login')
    def booking(request):
        conf=Configuracoes.objects.first()
        categorias=Categoria.objects.all()
        categoria=[]
        for marca in categorias:
            if marca.categoria_veiculos.all():
                categoria.append(marca)

        if  hasattr(request.user,'cliente'):

            return render(request, 'rentcar/cliente/booking.html',{
                'config':conf,
                'categorias':categoria,
            })
        return redirect('smart-login')
    
    @login_required(login_url='smart-login')
    def pedidos(request):
        conf=Configuracoes.objects.first()
        categoria=Categoria.objects.all()
        if  hasattr(request.user,'proprietario'):

            return render(request, 'rentcar/pedidos.html',{
                'config':conf,
                'categorias':categoria,
            })
        
        return redirect('smart-login')
    
    @login_required(login_url='smart-login')
    def update(request,pk):
        conf=Configuracoes.objects.first()
        categoria=Categoria.objects.all()
        pedido=get_object_or_404(Pedido, pk=pk)
        if  hasattr(request.user,'proprietario'):
            if request.method == 'POST':
                status = request.POST.get('status')
                nota = request.POST.get('nota')
                pedido.status=status
                pedido.observacao_dono=nota
                pedido.save()
                

                text=f'<span class="noti-title">{request.user.first_name} {request.user.last_name} </span> viu o seu pedido<span class="noti-title">, entre em contacto.</span>'
                
                notificacao=Notificacao.objects.create(
                    titulo=text,
                    user_receptor=pedido.cliente,
                    user_rementente=request.user,
                    user_rementente_viu=False
                )

                if notificacao:
                    messages.success(request,f'Pedido para o booking no veículo da placa {pedido.veiculo.placa} foi actualizado com sucesso.')
                
            return render(request, 'rentcar/pedido_modificar.html',{
                'config':conf,
                'categorias':categoria,
                'pedido':pedido,
            })
        
        return redirect('smart-login')
    
    @login_required(login_url='smart-login')
    def confirmar(request, placa):
        conf=Configuracoes.objects.first()
        if  hasattr(request.user,'cliente'):
            local_entrega = request.POST.get('local-entrega')
            coordenadas_entregas = str(request.POST.get('coordenadas_entregas'))
            local_devolucao = request.POST.get('local-devolucao')
            coordenadas_devolucao = str(request.POST.get('coordenadas_devolucao'))
            data_entrega = request.POST.get('datahoraentrega')
            data_devolucao = request.POST.get('datahoradevolucao')
            observacao = request.POST.get('observacao')
            distancia = request.POST.get('distancia')
            veiculo= get_object_or_404(Veiculo,url=placa)
            servico=get_object_or_404(Servicos,servico='Rentcar')
            
            # try:
            # Converter as strings em objetos datetime
            formato = "%Y-%m-%dT%H:%M"  # Ajuste o formato de acordo com o seu input
            # data_entrega = datetime.strptime(data_entrega, formato)
            # data_devolucao = datetime.strptime(data_devolucao, formato)

            lat1, lng1 = map(radians, [0,0])
            lat2, lng2 = map(radians, [0,0])

        
            if coordenadas_entregas:
                lat1, lng1 = map(float, coordenadas_devolucao.split(','))
            if coordenadas_devolucao:
                lat2, lng2 = map(float, coordenadas_devolucao.split(','))

            status=veiculo.verifica_distancias(radians(lat1),radians(lng1), radians(lat2), radians(lng2))

            if status:
                messages.error(request,f'Este veículo não pode ser entregue a esta distância de {distancia}Km.')
                return redirect('rentcar-reserva',veiculo.url)

            # Calcular a diferença em dias
            diferenca = data_devolucao - data_entrega
            duracao = f'{diferenca.days}'

            pedido=Pedido.objects.create(
                veiculo=veiculo,
                dono=veiculo.proprietario,
                cliente=request.user,
                data_entrega=data_entrega,
                data_devolucao=data_devolucao,
                observacao_cliente=observacao,
                local_entrega=local_entrega,
                local_devolucao=local_devolucao,
                duracao=duracao,
                distancia=distancia,
            )

            historico=Historico.objects.create(
                veiculo_rentcar=veiculo,
                servico=servico,
                cliente=request.user,
                profissional=veiculo.proprietario,
                local1=local_entrega,
                local2=local_devolucao,
                pedido=pedido,
            )

            text=f'<span class="noti-title">{request.user.first_name} {request.user.last_name} </span> fez um booking do veículo da placa <span class="noti-title">{veiculo.placa}</span>'
            if pedido:
                notificacao=Notificacao.objects.create(
                    titulo=text,
                    user_receptor=veiculo.proprietario,
                    user_rementente=request.user,
                    user_rementente_viu=False
                )

                if notificacao:
                    messages.success(request,f'Pedido para o booking no veículo da placa {veiculo.placa} foi submitido com sucesso.')
                
            return redirect('rentcar-home')
            
            # except Exception as e:
            #     messages.error(request,f'Erro ao processar o seu pedido, por favor tente novamente.')
            #     return redirect('rentcar-reserva',veiculo.url)
        
        return redirect('smart-login')

    @login_required(login_url='smart-login')
    def reservaTodas(request):
        pedidos= Pedido.objects.filter(dono=request.user)
        pedido=[]

        for p in pedidos:
            pedido.append({
                'foto_perfil_cliente': p.cliente.cliente.foto_perfil.url if p.cliente.cliente.foto_perfil else None,
                'nome_cliente': p.cliente.get_full_name(),
                'telefone':p.cliente.cliente.telefone,
                'is_status':True if p.status != 'Cancelado' and p.status == 'Pendente' else False,
                'status':p.status,
                'bg_status':'bg-danger' if p.status == 'Cancelado' else 'bg-success',
                'placa':p.veiculo.placa if p.veiculo.placa else None,
                'preco_estimativa': p.preco_estimativa(),
                'preco':f'{p.veiculo.preco} MT/{p.veiculo.condicao_aplicada}',
                'duracao':p.duracao,
                'veiculo': f'{p.veiculo.marca} {p.veiculo}',
                'distancia': p.distancia if p.distancia else 0,
                'local_entrega': p.local_entrega,
                'local_devolucao': p.local_devolucao,
                'data_entrega': format(p.data_entrega, 'd/m/Y H:i'),
                'data_devolucao':format(p.data_devolucao, 'd/m/Y H:i'),
                'pk':p.pk,
                'imagem_veiculo': p.veiculo.imagem_veiculo.url if p.veiculo.imagem_veiculo else None
            })

        return JsonResponse({'pendentes': pedido}, status=200)


    @login_required(login_url='smart-login')
    def reservaTotalPendentes(request):
        # Agrega contagens de pedidos e reservas em uma única consulta
        status_counts = Pedido.objects.filter(dono=request.user).values('status').annotate(count=Count('pk')).order_by('status')
        
        # Dicionários para fácil acesso
        pedido_counts = {status_count['status']: status_count['count'] for status_count in status_counts}
        
        # Extrai contagens específicas ou define como 0 se não existirem
        total_pd_pendente = pedido_counts.get('Pendente', 0)
        total_pd_cancelado = pedido_counts.get('cancelado', 0)

        return JsonResponse({'total': total_pd_pendente}, status=200)
    

    @login_required(login_url='smart-login')
    def reservaPendente(request):
        pedidos= Pedido.objects.filter(dono=request.user, status='Pendente').exclude(lida=True)[:1]
        pedido=[]
        for p in pedidos:
            pedido.append({
                'foto_perfil_cliente': p.cliente.cliente.foto_perfil.url if p.cliente.cliente.foto_perfil else None,
                'nome_cliente': p.cliente.get_full_name(),
                'telefone':p.cliente.cliente.telefone,
                'status':True if p.status != 'cancelado' and p.status == 'Pendente' else False,
                'placa':p.veiculo.placa if p.veiculo.placa else None,
                'preco_estimativa': p.preco_estimativa(),
                'preco':f'{p.veiculo.preco} MT/{p.veiculo.condicao_aplicada}',
                'duracao':p.duracao,
                'veiculo': f'{p.veiculo.marca} {p.veiculo}',
                'distancia': p.distancia if p.distancia else 0,
                'local_entrega': p.local_entrega,
                'local_devolucao': p.local_devolucao,
                'data_entrega': format(p.data_entrega, 'd/m/Y H:i'),
                'data_devolucao':format(p.data_devolucao, 'd/m/Y H:i'),
                'pk':p.pk,
                'imagem_veiculo': p.veiculo.imagem_veiculo.url if p.veiculo.imagem_veiculo else None
            })

        return JsonResponse({'pendentes': pedido}, status=200)

    @login_required(login_url='smart-login')
    def reservaPendenteLida(request,pk):
        pedidos= Pedido.objects.filter(dono=request.user, pk=pk, status='Pendente').update(lida=True)
        return JsonResponse({'success': 'success'}, status=200)

    @login_required(login_url='smart-login')
    def reservaPendenteCancelar(request,pk):
        motivo_cancelamento=request.GET.get('razao')
        pedidos= Pedido.objects.filter(dono=request.user, pk=pk, status='Pendente').update(lida=True,
            status='Cancelado',
            motivo_cancelamento=motivo_cancelamento
        )
        pedido=Pedido.objects.get(dono=request.user, pk=pk)
        historico=Historico.objects.filter(profissional=request.user, pedido=pedido).update(status='Cancelado')
        return JsonResponse({'success': 'success', 'message':'A reserva foi cancelada com sucesso.'}, status=200)

    @login_required(login_url='smart-login')
    def reservaPendenteAceitar(request,pk):
        pedidos= Pedido.objects.filter(dono=request.user, pk=pk, status='Pendente').update(lida=True,
            status='Aprovado',
            motivo_cancelamento="Pedido aprovado com sucesso."
        )
        pedido=Pedido.objects.get(dono=request.user, pk=pk)
        historico=Historico.objects.filter(profissional=request.user, pedido=pedido).update(status='Aprovado')

        return JsonResponse({'success': 'success', 'message':'A reserva foi aprovado com sucesso.'}, status=200)


# Notificacoes
class notificacao:
    @login_required(login_url='smart-login')
    def delete(request):
        Notificacao.objects.filter(user_receptor=request.user).delete()
        return redirect('rentcar-home')


# Proprietario
class proprietario:
    @login_required(login_url='smart-login')
    def dashboard(request):
        conf=Configuracoes.objects.first()
        categorias=Categoria.objects.all()
        categoria=[]
        for marca in categorias:
            if marca.categoria_veiculos.all():
                categoria.append(marca)
        if  hasattr(request.user,'proprietario'):
            return render(request, 'rentcar/minha_conta.html',{
                'config':conf,
                'categorias':categoria,
            })
        redirect('smart-login') 

    @login_required(login_url='smart-login')
    def minhaconta(request):
        conf=Configuracoes.objects.first()
        categorias=Categoria.objects.all()
        categoria=[]
        for marca in categorias:
            if marca.categoria_veiculos.all():
                categoria.append(marca)

        if  hasattr(request.user,'proprietario'):

            return render(request, 'rentcar/minha_conta.html',{
                'config':conf,
                'categorias':categoria,
            })
        redirect('smart-login')
    
    @login_required(login_url='smart-login')
    def modificarminhaconta(request):
        if  hasattr(request.user,'proprietario'):
            first_name=request.POST.get('nome')
            last_name=request.POST.get('sobrenome')
            email=request.POST.get('email')
            telefone=request.POST.get('telefone')
            localizacao=request.POST.get('localizacao')
            foto_perfil=request.FILES.get('imagem')

            user=request.user
            try:
                user.first_name=str(first_name).title()
                user.last_name=str(last_name).title()
                user.email=email
                user.save()
                if foto_perfil:
                    user.proprietario.foto_perfil=foto_perfil
                    
                user.proprietario.localizacao=localizacao
                user.proprietario.telefone=telefone
                user.proprietario.save()

                messages.success(request, f"{first_name} {last_name} Actualizado com sucesso.")
                return redirect('rentcar-dashboard-minha-conta')
            
            except Exception as e:
                messages.error(request, f"Erro ao actualizar o usuario {e}")
                return redirect('rentcar-dashboard-minha-conta')
            
            
        redirect('smart-login')


    @login_required(login_url='smart-login')
    def changeminhaconta(request):
        if  hasattr(request.user,'proprietario'):
            old_password=request.POST.get('old-passoword')
            password=request.POST.get('novo-password')
            user=User.objects.get(password=old_password, username=request.user)

            if user:
                
                user.set_password(password)

                messages.success(request, f"Passoword actualizado com sucesso.")
                return redirect('rentcar-dashboard-minha-conta')
            
            else:
                messages.error(request, f"O teu antingo passowrd é inválido.")
                return redirect('rentcar-dashboard-minha-conta')
            
            
        redirect('smart-login')

    @login_required(login_url='smart-login')
    def deleteminhaconta(request):
        if  hasattr(request.user,'proprietario'):
            request.user.delete()
            return redirect('rentcar-home')
        return redirect('smart-login')

# Rquests
class request:

    @login_required(login_url='smart-login')
    def request(request):
        if hasattr(request.user,'cliente') or not hasattr(request.user,'cliente'):
            local_entrega = request.POST.get('local-entrega')
            coordenadas_entregas = request.POST.get('coordenadas_entregas')
            local_devolucao = request.POST.get('local-devolucao')
            coordenadas_devolucao = request.POST.get('coordenadas_devolucao')
            aplicar = request.POST.get('aplicar') == 'on'
            categoria_id = request.POST.get('categoria')
            marca_id = request.POST.get('marca')
            combustivel= request.POST.get('combustivel')
            motorista = request.POST.get('motorista') == 'True'
            

            lat1, lng1 = map(radians, [0,0])
            lat2, lng2 = map(radians, [0,0])

        
            if coordenadas_entregas:
                lat1, lng1 = map(radians, coordenadas_entregas.split(','))
            if coordenadas_devolucao:
                lat2, lng2 = map(radians, coordenadas_devolucao.split(','))

            veiculo=[]
            veiculos=Veiculo.objects.all()
            if categoria_id or marca_id or combustivel or motorista and aplicar==True:
                
                categoria=Categoria.objects.filter(pk=categoria_id).first()
                veiculos=veiculos.filter(
                    Q(categoria=categoria) or
                    Q(combustivel=combustivel) or
                    Q(com_motorista=motorista)
                )

            for v in veiculos:
                status=v.verifica_distancias(radians(lat1),radians(lng1), radians(lat2), radians(lng2))
                
                if status:
                    if v.proprietario.proprietario.foto_perfil:
                        is_exists_image=True
                        foto_perfil=v.proprietario.proprietario.foto_perfil.url
                    else:
                        is_exists_image=False
                    
                    if v.imagem_veiculo:
                        is_exists_image_veiculo=True
                        imagem_veiculo=v.imagem_veiculo.url
                    else:
                        is_exists_image_veiculo=False

                    veiculo.append({
                        'pk': v.pk,
                        'marca': f'{v.marca}',
                        'modelo': f'{v.modelo}',
                        'preco': str(v.preco),
                        'condicao': v.condicao_aplicada,
                        'is_image_veiculo': bool(v.imagem_veiculo),
                        'imagem_veiculo': v.imagem_veiculo.url if v.imagem_veiculo else None,
                        'is_image_dono': bool(v.proprietario.proprietario.foto_perfil),
                        'foto_perfil': v.proprietario.proprietario.foto_perfil.url if v.proprietario.proprietario.foto_perfil else None,
                        'disponivel':bool(v.disponivel),
                        'telefone': v.proprietario.proprietario.telefone,
                        'solicitar': reverse('rentcar-reserva', args=[v.url]),
                        'localizacao': v.localizacao,
                    })
            
            return JsonResponse({'veiculos': veiculo}, safe=False)
        else:
            return redirect('smart-login')


    @login_required(login_url='smart-login')
    def reserva(request, placa):
        conf=Configuracoes.objects.first()
        veiculo=Veiculo.objects.get(url=placa)
        if hasattr(request.user,'cliente'):
            if request.method == 'POST':
                local_entrega = request.POST.get('local-entrega')
                coordenadas_entregas = request.POST.get('coordenadas_entregas')
                local_devolucao = request.POST.get('local-devolucao')
                coordenadas_devolucao = request.POST.get('coordenadas_devolucao')
                data_entrega = request.POST.get('data-entrega')
                hora_entrega = request.POST.get('hora-entrega')
                data_devolucao = request.POST.get('data-devolucao')
                hora_devolucao = request.POST.get('hora-devolucao')
                categoria_id = request.POST.get('categoria')
                marca_id = request.POST.get('marca')
                combustivel= request.POST.get('combustivel')
                motorista = request.POST.get('motorista') == 'True'

                if coordenadas_entregas:
                    lat1, lng1 = map(float, coordenadas_entregas.split(','))
                if coordenadas_devolucao:
                    lat2, lng2 = map(float, coordenadas_devolucao.split(','))

                veiculo=[]
                veiculos=Veiculo.objects.all()
                if categoria_id or marca_id or combustivel or motorista:
                    categoria=Categoria.filter(pk=categoria_id).first()
                    marca=Marca.filter(pk=marca_id).first()
                    veiculos.filter(
                        Q(categoria=categoria) |
                        Q(marca=marca) |
                        Q(combustivel=combustivel) |
                        Q(com_motorista=motorista)
                    )

                for v in veiculos:
                    status=v.verifica_distancias(float(lat1),float(lng1), float(lat2), float(lng2))
                    if status:
                        if v.proprietario.proprietario.foto_perfil:
                            is_exists_image=True
                            foto_perfil=v.proprietario.proprietario.foto_perfil.url
                        else:
                            is_exists_image=False
                        
                        if v.imagem_veiculo:
                            is_exists_image_veiculo=True
                            imagem_veiculo=v.imagem_veiculo.url
                        else:
                            is_exists_image_veiculo=False

                        veiculo.append({
                            'pk': v.pk,
                            'veiculo': f'{v.marca} {v.modelo}',
                            'foto_veiculo': v.imagem_veiculo.url if v.imagem_veiculo else None,
                            'preco': str(v.preco),
                            'condicao': v.condicao_aplicada,
                            'is_image_veiculo': bool(v.imagem_veiculo),
                            'imagem_veiculo': v.imagem_veiculo.url if v.imagem_veiculo else None,
                            'is_image_dono': bool(v.proprietario.proprietario.foto_perfil),
                            'foto_perfil': v.proprietario.proprietario.foto_perfil.url if v.proprietario.proprietario.foto_perfil else None,
                            'nome': v.proprietario.first_name,
                            'sabermais': reverse('rentcar-detalhe-veiculo', args=[v.url]),
                            'solicitar': reverse('rentcar-detalhe-veiculo', args=[v.url]),
                            'localizacao': v.localizacao,
                        })
                return JsonResponse({'veiculos': veiculo}, safe=False)
        
            else:
                return render(request, 'rentcar/cliente/reserva.html',{
                    'config':conf,
                    'veiculo':veiculo,
                    'titulo':'Reserva'
                })
        else:
            return redirect('smart-login')


    def historico(request,pk):
        conf=Configuracoes.objects.first()
        historico=Historico.objects.get(pk=pk)
        titulo='Histórico'
        if historico.status != 'Cancelado':

            return render(request, 'rentcar/cliente/historico_rentcar.html',{
                'config':conf,
                'historico':historico,
                'titulo':titulo,
            })
        else:
            return redirect('rentcar-home')
    
    def historicoCancelar(request,pk):
        conf=Configuracoes.objects.first()
        historico=get_object_or_404(Historico, pk=pk)
        historico.status='Cancelado'
        historico.save()
        pedido=get_object_or_404(Pedido, pk=historico.pedido.pk)
        pedido.status='Cancelado'
        pedido.save()
        return redirect('rentcar-home')
    

    

    






