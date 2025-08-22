from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import Lavagem, TipoLavagem, Base, TransporteEquipamento, Agendamento
from clientes.models import Cliente, Veiculo, Lavador
from .forms import BaseForm, TipoLavagemForm, TransporteEquipamentoForm
import json
from decimal import Decimal
from datetime import datetime
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")
    
    lavagens = Lavagem.objects.select_related(
        "lavador", "cliente"
    )
    
    if search_query:
        lavagens = lavagens.filter(
            Q(codigo__icontains=search_query) |
            Q(placa_veiculo__icontains=search_query) |
            Q(cliente__nome__icontains=search_query) |
            Q(lavador__nome__icontains=search_query)
        )
    
    if status_filter:
        lavagens = lavagens.filter(status=status_filter)
    
    lavagens_andamento = lavagens.filter(status="EM_ANDAMENTO").order_by("-hora_inicio")
    lavagens_concluidas = lavagens.filter(status="CONCLUIDA").order_by("-data_lavagem", "-hora_termino")
    
    paginator_andamento = Paginator(lavagens_andamento, 10)
    paginator_concluidas = Paginator(lavagens_concluidas, 20)
    
    page_andamento = request.GET.get("page_andamento", 1)
    page_concluidas = request.GET.get("page_concluidas", 1)
    
    lavagens_andamento = paginator_andamento.get_page(page_andamento)
    lavagens_concluidas = paginator_concluidas.get_page(page_concluidas)
    
    context = {
        "lavagens_andamento": lavagens_andamento,
        "lavagens_concluidas": lavagens_concluidas,
        "search_query": search_query,
        "status_filter": status_filter,
        "total_andamento": lavagens.filter(status="EM_ANDAMENTO").count(),
        "total_concluidas": lavagens.filter(status="CONCLUIDA").count(),
    }
    
    return render(request, "lavagens/dashboard.html", context)

@login_required
def nova_lavagem(request):
    if request.method == "POST":
        try:
            # --- CAPTURANDO DADOS COM OS NOMES CORRETOS DO HTML ---
            placa_veiculo = request.POST.get("placa_veiculo")
            base_id = request.POST.get("base")
            local = request.POST.get("local") # <-- CORRIGIDO: Agora busca "local"
            tipo_lavagem_id = request.POST.get("tipo_lavagem") # <-- CORRIGIDO: Agora busca "tipo_lavagem"
            transporte_id = request.POST.get("transporte_equipamento") # <-- CORRIGIDO: Agora busca "transporte_equipamento"
            lavador_id = request.POST.get("lavador")
            hora_inicio_str = request.POST.get("hora_inicio")
            observacoes = request.POST.get("observacoes", "")
            contrato = request.POST.get("contrato", "")
            valor_servico_str = request.POST.get("valor_servico")

            # --- VALIDAÇÃO (agora usando os nomes corretos) ---
            if not all([placa_veiculo, base_id, local, tipo_lavagem_id, transporte_id, hora_inicio_str]):
                messages.error(request, "Todos os campos com * devem ser preenchidos.")
                return redirect("nova_lavagem")

            # --- CONVERSÃO E BUSCA DE OBJETOS ---
            hora_inicio_obj = datetime.strptime(hora_inicio_str, '%Y-%m-%dT%H:%M')
            data_lavagem_obj = hora_inicio_obj.date()
            valor_servico = Decimal(valor_servico_str) if valor_servico_str else Decimal('0.00')
            
            base = get_object_or_404(Base, id=base_id)
            tipo_lavagem = get_object_or_404(TipoLavagem, id=tipo_lavagem_id) # Usará o ID correto
            transporte_equipamento = get_object_or_404(TransporteEquipamento, id=transporte_id) # Usará o ID correto
            lavador = get_object_or_404(Lavador, id=lavador_id) if lavador_id else None

            # --- CRIAÇÃO DO OBJETO LAVAGEM ---
            lavagem = Lavagem.objects.create(
                placa_veiculo=placa_veiculo.upper(),
                base=base,
                local=local,
                tipo_lavagem=tipo_lavagem,
                transporte_equipamento=transporte_equipamento,
                lavador=lavador,
                hora_inicio=hora_inicio_obj,
                hora_termino=None,
                data_lavagem=data_lavagem_obj,
                observacoes=observacoes,
                contrato=contrato,
                valor_servico=valor_servico,
            )
            
            messages.success(request, f"Lavagem {lavagem.codigo} criada com sucesso!")
            return redirect("dashboard")
            
        except Exception as e:
            messages.error(request, f"Erro ao criar lavagem: {str(e)}")
            return redirect("nova_lavagem")
    
    context = {
        "lavadores": Lavador.objects.filter(ativo=True),
        "tipos_lavagem": TipoLavagem.objects.all(),
        "bases": Base.objects.all(),
        "transportes_equipamentos": TransporteEquipamento.objects.all(),
    }
    
    return render(request, "lavagens/nova_lavagem.html", context)

@login_required
def detalhes_lavagem(request, lavagem_id):
    lavagem = get_object_or_404(Lavagem, id=lavagem_id)
    
    context = {
        "lavagem": lavagem,
    }
    
    return render(request, "lavagens/detalhes_lavagem.html", context)

@login_required
def concluir_lavagem(request, lavagem_id):
    if request.method == "POST":
        lavagem = get_object_or_404(Lavagem, id=lavagem_id)
        
        if lavagem.status == "EM_ANDAMENTO":
            # A lógica agora está no método do modelo, que já chamamos
            lavagem.concluir_lavagem() 
            messages.success(request, f"Lavagem {lavagem.codigo} concluída com sucesso!")
        else:
            messages.warning(request, "Esta lavagem já foi concluída ou cancelada.")
    
    return redirect("dashboard")

@login_required
def cancelar_lavagem(request, lavagem_id):
    if request.method == "POST":
        lavagem = get_object_or_404(Lavagem, id=lavagem_id)
        motivo = request.POST.get("motivo", "")
        
        if lavagem.status == "EM_ANDAMENTO":
            lavagem.cancelar_lavagem(motivo)
            messages.success(request, f"Lavagem {lavagem.codigo} cancelada.")
        else:
            messages.warning(request, "Esta lavagem já foi concluída ou cancelada.")
    
    return redirect("dashboard")

@login_required
@csrf_exempt
def api_locais_por_base(request):
    return JsonResponse({"locais": []})

@login_required
@csrf_exempt
def api_buscar_veiculo(request):
    if request.method == "GET":
        placa = request.GET.get("placa", "").upper()
        if placa:
            try:
                veiculo = Veiculo.objects.select_related("cliente").get(placa=placa)
                return JsonResponse({
                    "found": True,
                    "veiculo": {
                        "id": veiculo.id,
                        "marca": veiculo.marca,
                        "modelo": veiculo.modelo,
                        "ano": veiculo.ano,
                        "cor": veiculo.cor,
                        "tipo": veiculo.tipo,
                    },
                    "cliente": {
                        "id": veiculo.cliente.id,
                        "nome": veiculo.cliente.nome,
                        "telefone": veiculo.cliente.telefone,
                    } if veiculo.cliente else None
                })
            except Veiculo.DoesNotExist:
                return JsonResponse({"found": False})
    
    return JsonResponse({"found": False})


@login_required
def relatorios(request):
    from django.db.models import Count, Sum, Avg
    from decimal import Decimal
    import json
    
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")
    
    if not data_inicio or not data_fim:
        hoje = timezone.now().date()
        data_inicio = hoje.replace(day=1)
        data_fim = hoje
    else:
        data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
        data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
    
    lavagens_periodo = Lavagem.objects.filter(
        data_lavagem__range=[data_inicio, data_fim]
    )
    
    total_lavagens = lavagens_periodo.count()
    lavagens_em_andamento = lavagens_periodo.filter(status="EM_ANDAMENTO").count()
    lavagens_concluidas = lavagens_periodo.filter(status="CONCLUIDA").count()
    lavagens_canceladas = lavagens_periodo.filter(status="CANCELADA").count()
    
    faturamento_mes = lavagens_periodo.filter(status="CONCLUIDA").aggregate(
        total=Sum("valor_final")
    )["total"] or Decimal("0.00")
    
    faturamento_dia = Lavagem.objects.filter(
        status="CONCLUIDA",
        data_lavagem=timezone.now().date()
    ).aggregate(total=Sum("valor_final"))["total"] or Decimal("0.00")
    
    tempo_medio = 0
    
    lavagens_por_base = {}
    lavagens_por_tipo = {}
    
    from datetime import timedelta
    faturamento_labels = []
    faturamento_dados = []
    
    for i in range(30):
        data = timezone.now().date() - timedelta(days=i)
        faturamento_dia_grafico = Lavagem.objects.filter(
            status="CONCLUIDA",
            data_lavagem=data
        ).aggregate(total=Sum("valor_final"))["total"] or 0
        
        faturamento_labels.insert(0, data.strftime("%d/%m"))
        faturamento_dados.insert(0, float(faturamento_dia_grafico))
    
    ticket_medio = 0
    if lavagens_concluidas > 0:
        ticket_medio = faturamento_mes / lavagens_concluidas
    
    estatisticas = {
        "total_lavagens": total_lavagens,
        "lavagens_em_andamento": lavagens_em_andamento,
        "lavagens_concluidas": lavagens_concluidas,
        "lavagens_canceladas": lavagens_canceladas,
        "faturamento_mes": faturamento_mes,
        "faturamento_dia": faturamento_dia,
        "tempo_medio_lavagem": int(tempo_medio),
        "lavagens_por_base": lavagens_por_base,
        "lavagens_por_tipo": lavagens_por_tipo
    }
    
    context = {
        "estatisticas": estatisticas,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "ticket_medio": ticket_medio,
        "faturamento_labels": json.dumps(faturamento_labels),
        "faturamento_dados": json.dumps(faturamento_dados),
    }
    
    return render(request, "lavagens/relatorios.html", context)




@login_required
def base_list(request):
    bases = Base.objects.all()
    return render(request, 'lavagens/base_list.html', {'bases': bases})

@login_required
def base_create(request):
    if request.method == 'POST':
        form = BaseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Base adicionada com sucesso!')
            return redirect('base_list')
    else:
        form = BaseForm()
    return render(request, 'lavagens/base_form.html', {'form': form, 'action': 'Adicionar Base'})

@login_required
def base_update(request, pk):
    base = get_object_or_404(Base, pk=pk)
    if request.method == 'POST':
        form = BaseForm(request.POST, instance=base)
        if form.is_valid():
            form.save()
            messages.success(request, 'Base atualizada com sucesso!')
            return redirect('base_list')
    else:
        form = BaseForm(instance=base)
    return render(request, 'lavagens/base_form.html', {'form': form, 'action': 'Editar Base'})

@login_required
def base_delete(request, pk):
    base = get_object_or_404(Base, pk=pk)
    if request.method == 'POST':
        base.delete()
        messages.success(request, 'Base excluída com sucesso!')
        return redirect('base_list')
    return render(request, 'lavagens/base_confirm_delete.html', {'base': base})

@login_required
def tipo_lavagem_list(request):
    tipos_lavagem = TipoLavagem.objects.all()
    return render(request, 'lavagens/tipo_lavagem_list.html', {'tipos_lavagem': tipos_lavagem})

@login_required
def tipo_lavagem_create(request):
    if request.method == 'POST':
        form = TipoLavagemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de Lavagem adicionado com sucesso!')
            return redirect('tipo_lavagem_list')
    else:
        form = TipoLavagemForm()
    return render(request, 'lavagens/tipo_lavagem_form.html', {'form': form, 'action': 'Adicionar Tipo de Lavagem'})

@login_required
def tipo_lavagem_update(request, pk):
    tipo_lavagem = get_object_or_404(TipoLavagem, pk=pk)
    if request.method == 'POST':
        form = TipoLavagemForm(request.POST, instance=tipo_lavagem)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de Lavagem atualizado com sucesso!')
            return redirect('tipo_lavagem_list')
    else:
        form = TipoLavagemForm(instance=tipo_lavagem)
    return render(request, 'lavagens/tipo_lavagem_form.html', {'form': form, 'action': 'Editar Tipo de Lavagem'})

@login_required
def tipo_lavagem_delete(request, pk):
    tipo_lavagem = get_object_or_404(TipoLavagem, pk=pk)
    if request.method == 'POST':
        tipo_lavagem.delete()
        messages.success(request, 'Tipo de Lavagem excluído com sucesso!')
        return redirect('tipo_lavagem_list')
    return render(request, 'lavagens/tipo_lavagem_confirm_delete.html', {'tipo_lavagem': tipo_lavagem})

@login_required
def transporte_equipamento_list(request):
    transportes_equipamentos = TransporteEquipamento.objects.all()
    return render(request, 'lavagens/transporte_equipamento_list.html', {'transportes_equipamentos': transportes_equipamentos})

@login_required
def transporte_equipamento_create(request):
    if request.method == 'POST':
        form = TransporteEquipamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transporte/Equipamento adicionado com sucesso!')
            return redirect('transporte_equipamento_list')
    else:
        form = TransporteEquipamentoForm()
    return render(request, 'lavagens/transporte_equipamento_form.html', {'form': form, 'action': 'Adicionar Transporte/Equipamento'})

@login_required
def transporte_equipamento_update(request, pk):
    transporte_equipamento = get_object_or_404(TransporteEquipamento, pk=pk)
    if request.method == 'POST':
        form = TransporteEquipamentoForm(request.POST, instance=transporte_equipamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transporte/Equipamento atualizado com sucesso!')
            return redirect('transporte_equipamento_list')
    else:
        form = TransporteEquipamentoForm(instance=transporte_equipamento)
    return render(request, 'lavagens/transporte_equipamento_form.html', {'form': form, 'action': 'Editar Transporte/Equipamento'})

@login_required
def transporte_equipamento_delete(request, pk):
    transporte_equipamento = get_object_or_404(TransporteEquipamento, pk=pk)
    if request.method == 'POST':
        transporte_equipamento.delete()
        messages.success(request, 'Transporte/Equipamento excluído com sucesso!')
        return redirect('transporte_equipamento_list')
    return render(request, 'lavagens/transporte_equipamento_confirm_delete.html', {'transporte_equipamento': transporte_equipamento})


