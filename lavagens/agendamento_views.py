from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
import json
from clientes.models import Lavador
from decimal import Decimal

from .agendamento_models import Agendamento
from .agendamento_serializers import (
    AgendamentoListSerializer, AgendamentoDetailSerializer,
    AgendamentoCreateSerializer, AgendamentoUpdateSerializer,
    AgendamentoStatusSerializer, IniciarLavagemSerializer,
    AgendamentoCalendarioSerializer
)
from clientes.models import Cliente, Veiculo
from .models import Agendamento, Base, TipoLavagem, TransporteEquipamento


# Views Django tradicionais
def agendamentos_dashboard(request):
    status_filter = request.GET.get("status", "")
    data_filter = request.GET.get("data", "")
    busca = request.GET.get("busca", "")
    
    agendamentos = Agendamento.objects.select_related(
        "cliente", "veiculo", "base", "tipo_lavagem" # Mantém os outros select_related
    ).prefetch_related(
        "lavadores"  # ### CORREÇÃO AQUI ###
    ).all()

    
    if status_filter:
        agendamentos = agendamentos.filter(status=status_filter)
    
    if data_filter:
        try:
            data_obj = datetime.strptime(data_filter, "%Y-%m-%d").date()
            agendamentos = agendamentos.filter(data_agendamento=data_obj)
        except ValueError:
            pass
    
    if busca:
        agendamentos = agendamentos.filter(
            Q(codigo__icontains=busca) |
            Q(placa_veiculo__icontains=busca) |
            Q(cliente__nome__icontains=busca) |
            Q(telefone_contato__icontains=busca)
        )
    
    agendamentos = agendamentos.order_by("data_agendamento", "hora_agendamento")
    
    paginator = Paginator(agendamentos, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    hoje = timezone.now().date()
    stats = {
        "total": Agendamento.objects.count(),
        "hoje": Agendamento.objects.filter(data_agendamento=hoje).count(),
        "agendados": Agendamento.objects.filter(status="AGENDADO").count(),
        "confirmados": Agendamento.objects.filter(status="CONFIRMADO").count(),
        "vencidos": Agendamento.objects.filter(
            data_agendamento__lt=hoje,
            status__in=["AGENDADO", "CONFIRMADO"]
        ).count()
    }
    
    status_choices = Agendamento.STATUS_CHOICES
    
    context = {
        "page_obj": page_obj,
        "stats": stats,
        "status_choices": status_choices,
        "filtros": {
            "status": status_filter,
            "data": data_filter,
            "busca": busca
        }
    }
    
    return render(request, "lavagens/agendamentos_dashboard.html", context)

def novo_agendamento(request):
    """
    View para criar um novo agendamento.
    """
    # --- Lógica para quando o formulário é ENVIADO (método POST) ---
    if request.method == 'POST':
        try:
            # 1. Capturar dados do formulário
            cliente_id = request.POST.get('cliente')
            placa_veiculo = request.POST.get('placa_veiculo')
            data_agendamento_str = request.POST.get('data_agendamento')
            hora_agendamento_str = request.POST.get('hora_agendamento')
            base_id = request.POST.get('base')
            local = request.POST.get('local')
            tipo_lavagem_id = request.POST.get('tipo_lavagem')
            transporte_id = request.POST.get('transporte_equipamento')
            valor_estimado_str = request.POST.get('valor_estimado')

            # 2. Validação básica
            campos_obrigatorios = [cliente_id, placa_veiculo, data_agendamento_str, hora_agendamento_str, base_id, local, tipo_lavagem_id, transporte_id]
            if not all(campos_obrigatorios):
                messages.error(request, 'Erro: Todos os campos com * são obrigatórios.')
                return redirect('novo_agendamento')

            # 3. Converter dados para os tipos corretos
            data_agendamento_obj = datetime.strptime(data_agendamento_str, '%Y-%m-%d').date()
            hora_agendamento_obj = datetime.strptime(hora_agendamento_str, '%H:%M').time()
            valor_estimado_obj = Decimal(valor_estimado_str) if valor_estimado_str else None

            # 4. Buscar objetos relacionados no banco de dados
            cliente = get_object_or_404(Cliente, id=cliente_id)
            base = get_object_or_404(Base, id=base_id)
            tipo_lavagem = get_object_or_404(TipoLavagem, id=tipo_lavagem_id)
            transporte_equipamento = get_object_or_404(TransporteEquipamento, id=transporte_id)
            lavadores_ids = request.POST.getlist('lavadores') # Usar getlist e o nome do campo no plural

            # 5. Criar o objeto Agendamento com os campos corretos
            agendamento = Agendamento.objects.create(
                cliente=cliente,
                placa_veiculo=placa_veiculo.upper(),
                data_agendamento=data_agendamento_obj,
                hora_agendamento=hora_agendamento_obj,
                base=base,
                local=local,
                tipo_lavagem=tipo_lavagem,
                transporte_equipamento=transporte_equipamento,
                duracao_estimada=int(request.POST.get('duracao_estimada', 30)),
                prioridade=request.POST.get('prioridade', 'NORMAL'),
                telefone_contato=request.POST.get('telefone_contato', ''),
                email_contato=request.POST.get('email_contato', ''),
                observacoes=request.POST.get('observacoes', ''),
                status='AGENDADO',
                valor_estimado=valor_estimado_obj,
            )

            # ### CORREÇÃO 2: Use a variável 'agendamento' para chamar o .set() ###
            if lavadores_ids:
                agendamento.lavadores.set(lavadores_ids)

            messages.success(request, 'Agendamento criado com sucesso!')
            return redirect('agendamentos_dashboard')

        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao salvar: {e}")
            return redirect('novo_agendamento')

    # --- Lógica para quando a página é CARREGADA (método GET) ---
    else:
        # --- CORREÇÃO DE SINTAXE APLICADA AQUI ---
        context = {
            'clientes': Cliente.objects.filter(ativo=True),
            'bases': Base.objects.all(),
            'tipos_lavagem': TipoLavagem.objects.all(),
            'transportes_equipamentos': TransporteEquipamento.objects.all(),
            'lavadores': Lavador.objects.filter(ativo=True),
            'data_hoje': timezone.now().strftime('%Y-%m-%d'),
        }
        return render(request, 'lavagens/novo_agendamento.html', context)
    
    
def detalhes_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    context = {
        "agendamento": agendamento
    }
    
    return render(request, "lavagens/detalhes_agendamento.html", context)


@require_http_methods(["POST"])
def confirmar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    if agendamento.status == "AGENDADO":
        agendamento.confirmar_agendamento(confirmado_por=request.user.username)
        messages.success(request, f"Agendamento {agendamento.codigo} confirmado!")
    else:
        messages.error(request, "Este agendamento não pode ser confirmado.")
    
    return redirect("detalhes_agendamento", agendamento_id=agendamento_id)


@require_http_methods(["POST"])
def cancelar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    motivo = request.POST.get("motivo", "")
    
    if agendamento.pode_ser_cancelado:
        agendamento.cancelar_agendamento(motivo=motivo)
        messages.success(request, f"Agendamento {agendamento.codigo} cancelado!")
    else:
        messages.error(request, "Este agendamento não pode ser cancelado.")
    
    return redirect("detalhes_agendamento", agendamento_id=agendamento_id)


@require_http_methods(["POST"])
def iniciar_lavagem_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    try:
        if agendamento.pode_iniciar_lavagem:
            lavagem = agendamento.iniciar_lavagem()
            messages.success(request, f"Lavagem {lavagem.codigo} iniciada a partir do agendamento!")
            return redirect("detalhes_lavagem", lavagem_id=lavagem.id)
        else:
            messages.error(request, "Este agendamento não pode ser convertido em lavagem.")
    except Exception as e:
        messages.error(request, f"Erro ao iniciar lavagem: {str(e)}")
    
    return redirect("detalhes_agendamento", agendamento_id=agendamento_id)


def calendario_agendamentos(request):
    mes = request.GET.get("mes", timezone.now().month)
    ano = request.GET.get("ano", timezone.now().year)
    
    try:
        mes = int(mes)
        ano = int(ano)
    except (ValueError, TypeError):
        mes = timezone.now().month
        ano = timezone.now().year
    
    agendamentos = Agendamento.objects.filter(
        data_agendamento__year=ano,
        data_agendamento__month=mes
    ).select_related("cliente")
    
    context = {
        "mes": mes,
        "ano": ano,
        "agendamentos": agendamentos,
    }
    
    return render(request, "lavagens/calendario_agendamentos.html", context)


# APIs AJAX para frontend
@csrf_exempt
def api_locais_por_base(request):
    return JsonResponse({"locais": []})


@csrf_exempt
def api_verificar_disponibilidade(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            data_agendamento = data.get("data_agendamento")
            hora_agendamento = data.get("hora_agendamento")
            local = data.get("local")
            agendamento_id = data.get("agendamento_id")
            
            conflito = Agendamento.objects.filter(
                data_agendamento=data_agendamento,
                hora_agendamento=hora_agendamento,
                local=local,
                status__in=["AGENDADO", "CONFIRMADO"]
            )
            
            if agendamento_id:
                conflito = conflito.exclude(id=agendamento_id)
            
            disponivel = not conflito.exists()
            
            return JsonResponse({
                "disponivel": disponivel,
                "mensagem": "Horário disponível" if disponivel else "Horário já ocupado"
            })
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Método não permitido"}, status=405)


# ViewSet para API REST
class AgendamentoViewSet(viewsets.ModelViewSet):
    queryset = Agendamento.objects.select_related(
        "cliente", "veiculo", "lavador"
    ).all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == "list":
            return AgendamentoListSerializer
        elif self.action == "create":
            return AgendamentoCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return AgendamentoUpdateSerializer
        elif self.action == "calendario":
            return AgendamentoCalendarioSerializer
        else:
            return AgendamentoDetailSerializer
    
    def get_queryset(self):
        queryset = self.queryset
        
        status = self.request.query_params.get("status")
        data_inicio = self.request.query_params.get("data_inicio")
        data_fim = self.request.query_params.get("data_fim")
        busca = self.request.query_params.get("busca")
        
        if status:
            queryset = queryset.filter(status=status)
        
        if data_inicio:
            queryset = queryset.filter(data_agendamento__gte=data_inicio)
        
        if data_fim:
            queryset = queryset.filter(data_agendamento__lte=data_fim)
        
        if busca:
            queryset = queryset.filter(
                Q(codigo__icontains=busca) |
                Q(placa_veiculo__icontains=busca) |
                Q(cliente__nome__icontains=busca)
            )
        
        return queryset.order_by("data_agendamento", "hora_agendamento")
    
    @action(detail=True, methods=["post"])
    def confirmar(self, request, pk=None):
        agendamento = self.get_object()
        serializer = AgendamentoStatusSerializer(
            data=request.data, 
            context={"agendamento": agendamento}
        )
        
        if serializer.is_valid():
            confirmado_por = serializer.validated_data.get("confirmado_por", request.user.username)
            agendamento.confirmar_agendamento(confirmado_por=confirmado_por)
            return Response({"message": "Agendamento confirmado com sucesso"})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        agendamento = self.get_object()
        serializer = AgendamentoStatusSerializer(
            data=request.data,
            context={"agendamento": agendamento}
        )
        
        if serializer.is_valid():
            motivo = serializer.validated_data.get("motivo", "")
            agendamento.cancelar_agendamento(motivo=motivo)
            return Response({"message": "Agendamento cancelado com sucesso"})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=["post"])
    def iniciar_lavagem(self, request, pk=None):
        agendamento = self.get_object()
        serializer = IniciarLavagemSerializer(
            data=request.data,
            context={"agendamento": agendamento}
        )
        
        if serializer.is_valid():
            try:
                lavagem = agendamento.iniciar_lavagem()
                
                obs_adicionais = serializer.validated_data.get("observacoes_adicionais")
                if obs_adicionais:
                    lavagem.observacoes = f"{lavagem.observacoes}\n{obs_adicionais}".strip()
                    lavagem.save()
                
                return Response({
                    "message": "Lavagem iniciada com sucesso",
                    "lavagem_id": lavagem.id,
                    "lavagem_codigo": lavagem.codigo
                })
            except Exception as e:
                return Response(
                    {"error": str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=["get"])
    def calendario(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def estatisticas(self, request):
        hoje = timezone.now().date()
        
        stats = {
            "total": self.get_queryset().count(),
            "hoje": self.get_queryset().filter(data_agendamento=hoje).count(),
            "por_status": dict(
                self.get_queryset().values("status").annotate(
                    count=Count("id")
                ).values_list("status", "count")
            ),
            "vencidos": self.get_queryset().filter(
                data_agendamento__lt=hoje,
                status__in=["AGENDADO", "CONFIRMADO"]
            ).count()
        }
        return Response(stats)


