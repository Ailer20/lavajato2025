from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Produto, MovimentacaoEstoque, NotaFiscalEntrada
# AQUI ESTAVA O ERRO: Importamos os forms corretos agora
from .forms import ProdutoForm, NotaFiscalForm, SaidaUnificadaForm, DevolverMaterialForm

from .models import Categoria, LocalArmazenamento
from .forms import CategoriaForm, LocalArmazenamentoForm

@login_required
def estoque_lista(request):
    produtos = Produto.objects.select_related('localizacao', 'categoria').all().order_by('nome')
    alertas = [p for p in produtos if p.quantidade_atual <= p.estoque_minimo]
    
    return render(request, 'gestao/estoque_lista.html', {
        'produtos': produtos,
        'alertas': alertas
    })

@login_required
def historico_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    movimentacoes = MovimentacaoEstoque.objects.filter(produto=produto).order_by('-data_movimento')
    
    return render(request, 'gestao/historico_produto.html', {
        'produto': produto,
        'movimentacoes': movimentacoes
    })

@login_required
def registrar_saida(request):
    """
    Tela ÚNICA de Saída.
    Serve tanto para Uso Interno (sem responsável) quanto para Atribuição (com responsável).
    """
    if request.method == 'POST':
        form = SaidaUnificadaForm(request.POST)
        if form.is_valid():
            mov = form.save(commit=False)
            mov.tipo = 'SAIDA'
            mov.usuario_sistema = request.user
            
            try:
                mov.save()
                
                # Mensagem personalizada dependendo do caso
                if mov.responsavel:
                    messages.success(request, f"Material entregue para {mov.responsavel.nome} com sucesso!")
                else:
                    messages.success(request, f"Baixa de estoque registrada com sucesso!")
                    
                return redirect('estoque_lista')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = SaidaUnificadaForm()
    
    return render(request, 'gestao/saida_unificada.html', {
        'form': form
    })

@login_required
def meu_estoque_pessoal(request):
    """Tela do Colaborador para ver o que está com ele"""
    try:
        lavador = request.user.lavador_perfil
    except:
        messages.error(request, "Seu usuário não está vinculado a um perfil de Colaborador.")
        return redirect('dashboard')

    # 1. Pegar saídas para ele
    recebidos = MovimentacaoEstoque.objects.filter(
        responsavel=lavador, 
        tipo='SAIDA'
    ).values('produto').annotate(qtd_recebida=Sum('quantidade'))
    
    # 2. Pegar devoluções dele
    devolvidos = MovimentacaoEstoque.objects.filter(
        responsavel=lavador, 
        tipo='DEVOLUCAO'
    ).values('produto').annotate(qtd_devolvida=Sum('quantidade'))

    estoque_pessoal = []
    mapa_devolucoes = {item['produto']: item['qtd_devolvida'] for item in devolvidos}
    
    for item in recebidos:
        produto_id = item['produto']
        qtd_rec = item['qtd_recebida']
        qtd_dev = mapa_devolucoes.get(produto_id, 0)
        saldo = qtd_rec - qtd_dev
        
        if saldo > 0:
            produto = Produto.objects.get(id=produto_id)
            estoque_pessoal.append({
                'produto': produto,
                'quantidade': saldo
            })

    return render(request, 'gestao/meu_estoque.html', {
        'estoque': estoque_pessoal,
        'lavador': lavador
    })

@login_required
def registrar_devolucao(request):
    """Tela do Colaborador para devolver item"""
    try:
        lavador = request.user.lavador_perfil
    except:
        messages.error(request, "Acesso negado. Vincule seu usuário a um colaborador.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = DevolverMaterialForm(lavador, request.POST)
        if form.is_valid():
            produto = form.cleaned_data['produto']
            qtd_devolver = form.cleaned_data['quantidade']
            
            # Validação de saldo
            total_recebido = MovimentacaoEstoque.objects.filter(
                responsavel=lavador, tipo='SAIDA', produto=produto
            ).aggregate(total=Sum('quantidade'))['total'] or 0
            
            total_devolvido = MovimentacaoEstoque.objects.filter(
                responsavel=lavador, tipo='DEVOLUCAO', produto=produto
            ).aggregate(total=Sum('quantidade'))['total'] or 0
            
            saldo_atual = total_recebido - total_devolvido
            
            if qtd_devolver > saldo_atual:
                messages.error(request, f"Erro: Você só possui {saldo_atual} unidades de {produto.nome}.")
            else:
                mov = form.save(commit=False)
                mov.tipo = 'DEVOLUCAO'
                mov.responsavel = lavador
                mov.usuario_sistema = request.user
                mov.save()
                messages.success(request, "Devolução realizada com sucesso.")
                return redirect('meu_estoque_pessoal')
    else:
        form = DevolverMaterialForm(lavador)

    return render(request, 'gestao/devolver_material.html', {'form': form})

@login_required
def produto_create(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto cadastrado!')
            return redirect('estoque_lista')
    else:
        form = ProdutoForm()
    return render(request, 'gestao/produto_form.html', {'form': form, 'titulo': 'Novo Produto'})

@login_required
def produto_update(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado!')
            return redirect('estoque_lista')
        else:
            # ADICIONE ISTO PARA VER O ERRO NO TERMINAL
            print(form.errors) 
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'gestao/produto_form.html', {'form': form, 'titulo': 'Editar Produto'})

    
@login_required
def nota_fiscal_lista(request):
    notas = NotaFiscalEntrada.objects.all().order_by('-data_emissao')
    return render(request, 'gestao/nota_fiscal_lista.html', {'notas': notas})

@login_required
def nota_fiscal_create(request):
    if request.method == 'POST':
        form = NotaFiscalForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nota Fiscal lançada com sucesso!')
            return redirect('nota_fiscal_lista')
    else:
        form = NotaFiscalForm()
    return render(request, 'gestao/nota_fiscal_form.html', {'form': form})


# --- CATEGORIAS ---
@login_required
def categoria_lista(request):
    categorias = Categoria.objects.all().order_by('nome')
    return render(request, 'gestao/categoria_lista.html', {'categorias': categorias})

@login_required
def categoria_create(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm()
    return render(request, 'gestao/categoria_form.html', {'form': form, 'titulo': 'Nova Categoria'})

@login_required
def categoria_update(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada!')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'gestao/categoria_form.html', {'form': form, 'titulo': 'Editar Categoria'})

# --- LOCAIS DE ARMAZENAMENTO ---
@login_required
def local_lista(request):
    locais = LocalArmazenamento.objects.all().order_by('nome')
    return render(request, 'gestao/local_lista.html', {'locais': locais})

@login_required
def local_create(request):
    if request.method == 'POST':
        form = LocalArmazenamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Local criado com sucesso!')
            return redirect('local_lista')
    else:
        form = LocalArmazenamentoForm()
    return render(request, 'gestao/local_form.html', {'form': form, 'titulo': 'Novo Local'})

@login_required
def local_update(request, pk):
    local = get_object_or_404(LocalArmazenamento, pk=pk)
    if request.method == 'POST':
        form = LocalArmazenamentoForm(request.POST, instance=local)
        if form.is_valid():
            form.save()
            messages.success(request, 'Local atualizado!')
            return redirect('local_lista')
    else:
        form = LocalArmazenamentoForm(instance=local)
    return render(request, 'gestao/local_form.html', {'form': form, 'titulo': 'Editar Local'})