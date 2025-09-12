from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import Lavagem, TipoLavagem, Base, TransporteEquipamento, Agendamento, MaterialLavagem
from clientes.models import Cliente, Veiculo, Lavador
from .forms import BaseForm, TipoLavagemForm, TransporteEquipamentoForm, MaterialLavagemFormSet
import json
# Alternativa recomendada
from django.db import models
from django.db.models import Q, Count, Sum, Avg

from decimal import Decimal
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
# Linha CORRIGIDA para colocar no seu views.py

from .models import Lavagem, Base, TipoLavagem
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
    data_inicio_str = request.GET.get("data_inicio")
    data_fim_str = request.GET.get("data_fim")
    base_filtro_id = request.GET.get("base_filtro") # Captura o ID da base para filtro

    hoje = timezone.now().date()

    # Definir datas padrão se não forem fornecidas
    if not data_inicio_str or not data_fim_str:
        data_inicio = hoje.replace(day=1) # Início do mês atual
        data_fim = hoje
    else:
        data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()
        data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date()
    
    # Filtrar lavagens pelo período
    lavagens_periodo = Lavagem.objects.filter(
        data_lavagem__range=[data_inicio, data_fim]
    )

    # Aplicar filtro de base, se houver
    if base_filtro_id:
        lavagens_periodo = lavagens_periodo.filter(base_id=base_filtro_id)
    
    # --- Cálculos de Estatísticas ---
    total_lavagens = lavagens_periodo.count()
    lavagens_em_andamento = lavagens_periodo.filter(status="EM_ANDAMENTO").count()
    lavagens_concluidas = lavagens_periodo.filter(status="CONCLUIDA").count()
    lavagens_canceladas = lavagens_periodo.filter(status="CANCELADA").count()
    
    faturamento_mes = lavagens_periodo.filter(status="CONCLUIDA").aggregate(
        total=Sum("valor_final")
    )["total"] or Decimal("0.00")
    
    faturamento_dia = Lavagem.objects.filter(
        status="CONCLUIDA",
        data_lavagem=hoje # Faturamento do dia atual
    ).aggregate(total=Sum("valor_final"))["total"] or Decimal("0.00")
    
    # Tempo médio de lavagem (apenas para lavagens concluídas com hora de início e término)
    tempo_medio_lavagem_segundos = lavagens_periodo.filter(
        status="CONCLUIDA",
        hora_inicio__isnull=False,
        hora_termino__isnull=False
    ).annotate(
        duracao_segundos=(models.F('hora_termino') - models.F('hora_inicio'))
    ).aggregate(
        avg_duracao=Avg('duracao_segundos')
    )['avg_duracao']

    tempo_medio = int(tempo_medio_lavagem_segundos.total_seconds() / 60) if tempo_medio_lavagem_segundos else 0
    
    # --- Dados para o Gráfico de Lavagens por Base ---
    lavagens_por_base_query = (
        lavagens_periodo
        .filter(base__isnull=False) # Garante que só bases válidas sejam contadas
        .values('base__nome')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    lavagens_por_base = {item['base__nome']: item['total'] for item in lavagens_por_base_query}

    # --- Dados para o Gráfico de Lavagens por Tipo (se você for usar) ---
    lavagens_por_tipo_query = (
        lavagens_periodo
        .filter(tipo_lavagem__isnull=False) # Garante que só tipos válidos sejam contados
        .values('tipo_lavagem__nome')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    lavagens_por_tipo = {item['tipo_lavagem__nome']: item['total'] for item in lavagens_por_tipo_query}
    
    # --- Dados para o Gráfico de Faturamento por Período (Linha) ---
    faturamento_labels = []
    faturamento_dados = []
    
    # Gerar labels e dados para cada dia no período selecionado
    delta = data_fim - data_inicio
    for i in range(delta.days + 1):
        dia = data_inicio + timedelta(days=i)
        faturamento_dia_grafico = lavagens_periodo.filter(
            status="CONCLUIDA",
            data_lavagem=dia
        ).aggregate(total=Sum("valor_final"))["total"] or 0
        
        faturamento_labels.append(dia.strftime("%d/%m"))
        faturamento_dados.append(float(faturamento_dia_grafico))
    
    # --- Ticket Médio ---
    ticket_medio = 0
    if lavagens_concluidas > 0:
        ticket_medio = faturamento_mes / lavagens_concluidas
    
    # --- Performance dos Lavadores ---
    performance_lavadores = lavagens_periodo.filter(status="CONCLUIDA", lavador__isnull=False)\
        .values("lavador__nome")\
        .annotate(total_lavagens_concluidas=Count("id"))\
        .order_by("-total_lavagens_concluidas")

    lavadores_labels = [item['lavador__nome'] for item in performance_lavadores]
    lavadores_dados = [item['total_lavagens_concluidas'] for item in performance_lavadores]

    # --- Ranking de Carros/Contratos ---
    ranking_carros_contratos = lavagens_periodo.filter(status="CONCLUIDA")\
        .values("placa_veiculo", "contrato")\
        .annotate(total_lavagens=Count("id"))\
        .order_by("-total_lavagens")[:10] # Top 10

    ranking_labels = [f"{item['placa_veiculo']} ({item['contrato'] if item['contrato'] else 'N/A'})" for item in ranking_carros_contratos]
    ranking_dados = [item['total_lavagens'] for item in ranking_carros_contratos]

    # --- Consumo de Materiais por Mês ---
    # Esta parte será mais complexa e precisará de um loop ou agregação mais avançada
    # para somar os materiais de cada tipo de lavagem associada às lavagens concluídas.
    # Por enquanto, vamos deixar como um placeholder.
    consumo_materiais = {}
    # Para cada lavagem concluída no período, somar os materiais do tipo de lavagem associado
    for lavagem in lavagens_periodo.filter(status="CONCLUIDA").select_related("tipo_lavagem").prefetch_related("tipo_lavagem__materiais"):
        if lavagem.tipo_lavagem:
            for material in lavagem.tipo_lavagem.materiais.all():
                consumo_materiais[material.nome] = consumo_materiais.get(material.nome, Decimal('0.00')) + material.valor

    materiais_labels = list(consumo_materiais.keys())
    materiais_dados = [float(value) for value in consumo_materiais.values()]

    # --- Lavagens por Contrato ---
    lavagens_por_contrato = lavagens_periodo.filter(status="CONCLUIDA", contrato__isnull=False)\
        .values("contrato")\
        .annotate(total_lavagens=Count("id"))\
        .order_by("-total_lavagens")

    contrato_labels = [item["contrato"] for item in lavagens_por_contrato]
    contrato_dados = [item["total_lavagens"] for item in lavagens_por_contrato]

    # --- Lavagens por Transporte/Equipamento ---
    lavagens_por_transporte = lavagens_periodo.filter(status="CONCLUIDA", transporte_equipamento__isnull=False)\
        .values("transporte_equipamento__nome")\
        .annotate(total_lavagens=Count("id"))\
        .order_by("-total_lavagens")

    transporte_labels = [item["transporte_equipamento__nome"] for item in lavagens_por_transporte]
    transporte_dados = [item["total_lavagens"] for item in lavagens_por_transporte]

    # --- Contexto para o Template ---
    estatisticas = {
        "total_lavagens": total_lavagens,
        "lavagens_em_andamento": lavagens_em_andamento,
        "lavagens_concluidas": lavagens_concluidas,
        "lavagens_canceladas": lavagens_canceladas,
        "faturamento_mes": faturamento_mes,
        "faturamento_dia": faturamento_dia,
        "tempo_medio_lavagem": tempo_medio,
        "lavagens_por_base": lavagens_por_base,
        "lavagens_por_tipo": lavagens_por_tipo,
    }
    
    # Obter todas as bases para o filtro do template
    bases_disponiveis = Base.objects.all().order_by('nome')

    context = {
        "estatisticas": estatisticas,
        "data_inicio": data_inicio.strftime('%Y-%m-%d'),
        "data_fim": data_fim.strftime('%Y-%m-%d'),
        "ticket_medio": ticket_medio,
        "faturamento_labels": json.dumps(faturamento_labels),
        "faturamento_dados": json.dumps(faturamento_dados),
        "bases": bases_disponiveis,
        "base_filtro": base_filtro_id,
        "lavadores_labels": json.dumps(lavadores_labels),
        "lavadores_dados": json.dumps(lavadores_dados),
        "ranking_labels": json.dumps(ranking_labels),
        "ranking_dados": json.dumps(ranking_dados),
        "materiais_labels": json.dumps(materiais_labels),
        "materiais_dados": json.dumps(materiais_dados),
        "contrato_labels": json.dumps(contrato_labels),
        "contrato_dados": json.dumps(contrato_dados),
        "transporte_labels": json.dumps(transporte_labels),
        "transporte_dados": json.dumps(transporte_dados),
        "ranking_carros_contratos": ranking_carros_contratos,

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
        formset = MaterialLavagemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            tipo_lavagem = form.save()
            formset.instance = tipo_lavagem
            formset.save()
            messages.success(request, 'Tipo de Lavagem e materiais adicionados com sucesso!')
            return redirect('tipo_lavagem_list')
    else:
        form = TipoLavagemForm()
        formset = MaterialLavagemFormSet()
    return render(request, 'lavagens/tipo_lavagem_form.html', {'form': form, 'formset': formset, 'action': 'Adicionar Tipo de Lavagem'})

@login_required
def tipo_lavagem_update(request, pk):
    tipo_lavagem = get_object_or_404(TipoLavagem, pk=pk)
    if request.method == 'POST':
        form = TipoLavagemForm(request.POST, instance=tipo_lavagem)
        formset = MaterialLavagemFormSet(request.POST, instance=tipo_lavagem)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Tipo de Lavagem e materiais atualizados com sucesso!')
            return redirect('tipo_lavagem_list')
    else:
        form = TipoLavagemForm(instance=tipo_lavagem)
        formset = MaterialLavagemFormSet(instance=tipo_lavagem)
    return render(request, 'lavagens/tipo_lavagem_form.html', {'form': form, 'formset': formset, 'action': 'Editar Tipo de Lavagem'})

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


