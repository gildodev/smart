from django.shortcuts import render,get_object_or_404,redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth import login,logout,authenticate
from .models import *
from .ninjaAPI import *

# Create your views here.
# Usuario
class index:
    def index(request):
        conf=Configuracoes.objects.first()
        return render(request, 'index.html',{
            'config': conf
        })

class auth:
    def Login(request):
        conf=Configuracoes.objects.first()
        if request.method == "GET":
            return render(request,'auth/login.html',{'config':conf})
        else: 
            password=request.POST.get('password')
            username=request.POST.get('username')
            try:
                user = authenticate(request,username=username,password=password)
                if user is not None:
                    login(request,user)
                    if hasattr(user,'proprietario'):
                        return redirect('rentcar-home')
                    elif hasattr(user, 'cliente'):
                        return redirect('rentcar-home')
                else:
                    messages.error(request, "Dados credenciais inválidos, tente novamente!")
                    return redirect('smart-login')
                
            except Exception as e:
                messages.error(request, f"Dados credenciais inválidos, tente novamente!{e}")
                return redirect('smart-login')
            
    def cadastro(request):
        config_site = Configuracoes.objects.first()
        if request.method == "GET":
            return render(request,'auth/cadastro.html',{'config':config_site})
        else: 
            first_name=request.POST.get('nome')
            last_name=request.POST.get('sobrenome')
            password=request.POST.get('password')
            email=request.POST.get('email')
            username=request.POST.get('username')
            telefone=request.POST.get('telefone')
            servico=request.POST.get('servico')
            
            try:
                user=User.objects.filter(username=username)
                if user:
                    messages.error(request, "Username  já cadastrado, tente novamente!")
                    return redirect('smart-cadastro')
                
            except Exception as e:
                messages.error(request, f"Erro: {e}")
                return redirect('smart-cadastro')
            try:
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    first_name=first_name.title(), 
                    password=password,
                    last_name=last_name.title(),
                )

                if user:
                    if servico =='cliente':
                        cliente= Cliente.objects.create(
                            user=user,
                            telefone=telefone
                        )

                        login(request, user)
                        return redirect('rentcar-home')
                    elif servico =='delivery':
                        cliente= Delivery.objects.create(
                            user=user,
                            telefone=telefone
                        )

                        login(request, user)
                        return redirect('rentcar-home')
                    elif servico =='taxi':
                        cliente= Motorista.objects.create(
                            user=user,
                            telefone=telefone
                        )

                        login(request, user)
                        return redirect('rentcar-home')
                    elif servico =='rentcar':
                        cliente= Proprietario.objects.create(
                            user=user,
                            telefone=telefone
                        )

                        login(request, user)
                        return redirect('rentcar-home')
                    else:
                        messages.error(request, f"Serviço {servico} é inválido. Por favor, tente novamente!")
                        user.delete()
                        return redirect('smart-cadastro')
                    
            except Exception as e:
                user.delete()
                messages.error(request, f"Erro: {e}")
                return redirect('smart-cadastro')

    @api_view(['POST'])
    def clienteAPI(request):
        first_name=request.POST.get('nome')
        last_name=request.POST.get('sobrenome')
        password=request.POST.get('password')
        email=request.POST.get('email')
        username=request.POST.get('username')
        telefone=request.POST.get('telefone')
        
        try:
            user=User.objects.filter(username=username)
            if user:
                return Response({'success': False, 'message': 'Estes dados do usuário já existem, por favor, inicie sessão.'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'success': False, 'message': f'{e}.'}, status=status.HTTP_400_BAD_REQUEST)
       
        try:
            user = User.objects.create_user(
                email=email,
                username=username,
                first_name=first_name.title(), 
                password=password,
                last_name=last_name.title(),
            )

            if user:
                cliente= Cliente.objects.create(
                    user=user,
                    telefone=telefone
                )

                if cliente is not None:
                    login(request, user)
                    return Response({'success': True, 'redirect_url': '/rentcar/'}, status=status.HTTP_200_OK)
                else:
                    user.delete()
                    return Response({'success': False, 'message': f'Erro.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'success': False, 'message': f'Erro.'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            user.delete()
            return Response({'success': False, 'message': f'{e}.'}, status=status.HTTP_400_BAD_REQUEST)
            
    def cliente(request):
        config_site = Configuracoes.objects.first()
        return render(request,'auth/cadastro_cliente.html',{'config':config_site})
        
    @api_view(['POST'])
    def ProfissionalAPI(request):
        data = request.data
        first_name = data.get('nome')
        last_name = data.get('sobrenome')
        password = data.get('password')
        email = data.get('email')
        username = data.get('username')
        telefone = data.get('telefone')
        servico = data.get('servico')

        if not all([first_name, last_name, password, email, username, telefone, servico]):
            return Response({'success': False, 'message': 'Todos os campos são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'success': False, 'message': 'Este usuário já existe. Por favor, inicie sessão.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.create_user(
                email=email,
                username=username,
                first_name=first_name.title(), 
                password=password,
                last_name=last_name.title(),
            )
            prof=None
            
            service = Servicos.objects.filter(servico=servico).first()
            if not service:
                user.delete()
                return Response({'success': False, 'message': 'Serviço inválido. Por favor, tente novamente!'}, status=status.HTTP_400_BAD_REQUEST)
            
            if servico == 'Rentcar':
                prof = Proprietario.objects.create(
                    user=user,
                    servico=service,
                    telefone=telefone,
                )
            elif servico == 'Taxi':
                prof = Taxi.objects.create(
                    user=user,
                    servico=service,
                    telefone=telefone,
                )
            else:
                prof = Delivery.objects.create(
                    user=user,
                    servico=service,
                    telefone=telefone,
                )

            if prof:
                login(request, user)
                return Response({'success': True, 'redirect_url': '/rentcar/'}, status=status.HTTP_200_OK)
            else:
                user.delete()
                return Response({'success': False, 'message': f'Erro ao criar a conta {servico}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            if user:
                user.delete()
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def profissional(request):
        config_site = Configuracoes.objects.first()
        servicos=Servicos.objects.all()
        return render(request,'auth/cadastro_profissional.html',{
            'config':config_site,
            'servicos':servicos,
        })
        

    @login_required(login_url='smart-login')  # Substitua 'login' pela URL da página de login
    def Logout(request):
        logout(request)
        return render(request,'auth/login.html')
    
    @api_view(['POST'])
    def login_view(request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'success': True, 'redirect_url': '/rentcar/'}, status=status.HTTP_200_OK)

        else:
            return JsonResponse({'success': False, 'message': 'Dados de acesso incorrectos, tente novamente.'}, status=status.HTTP_400_BAD_REQUEST)

