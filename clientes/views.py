from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cliente, Veiculo, Lavador
from .forms import ClienteForm, VeiculoForm, LavadorForm

# Views para Cliente
def cliente_list(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes/cliente_list.html', {'clientes': clientes})

def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente adicionado com sucesso!')
            return redirect('cliente_list')
    else:
        form = ClienteForm()
    return render(request, 'clientes/cliente_form.html', {'form': form, 'action': 'Adicionar Cliente'})

def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('cliente_list')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/cliente_form.html', {'form': form, 'action': 'Editar Cliente'})

def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente excluído com sucesso!')
        return redirect('cliente_list')
    return render(request, 'clientes/cliente_confirm_delete.html', {'cliente': cliente})

# Views para Veiculo
def veiculo_list(request):
    veiculos = Veiculo.objects.all()
    return render(request, 'clientes/veiculo_list.html', {'veiculos': veiculos})

def veiculo_create(request):
    if request.method == 'POST':
        form = VeiculoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Veículo adicionado com sucesso!')
            return redirect('veiculo_list')
    else:
        form = VeiculoForm()
    return render(request, 'clientes/veiculo_form.html', {'form': form, 'action': 'Adicionar Veículo'})

def veiculo_update(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == 'POST':
        form = VeiculoForm(request.POST, instance=veiculo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Veículo atualizado com sucesso!')
            return redirect('veiculo_list')
    else:
        form = VeiculoForm(instance=veiculo)
    return render(request, 'clientes/veiculo_form.html', {'form': form, 'action': 'Editar Veículo'})

def veiculo_delete(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == 'POST':
        veiculo.delete()
        messages.success(request, 'Veículo excluído com sucesso!')
        return redirect('veiculo_list')
    return render(request, 'clientes/veiculo_confirm_delete.html', {'veiculo': veiculo})

# Views para Lavador
def lavador_list(request):
    lavadores = Lavador.objects.all()
    return render(request, 'clientes/lavador_list.html', {'lavadores': lavadores})

def lavador_create(request):
    if request.method == 'POST':
        form = LavadorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lavador adicionado com sucesso!')
            return redirect('lavador_list')
    else:
        form = LavadorForm()
    return render(request, 'clientes/lavador_form.html', {'form': form, 'action': 'Adicionar Lavador'})

def lavador_update(request, pk):
    lavador = get_object_or_404(Lavador, pk=pk)
    if request.method == 'POST':
        form = LavadorForm(request.POST, instance=lavador)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lavador atualizado com sucesso!')
            return redirect('lavador_list')
    else:
        form = LavadorForm(instance=lavador)
    return render(request, 'clientes/lavador_form.html', {'form': form, 'action': 'Editar Lavador'})

def lavador_delete(request, pk):
    lavador = get_object_or_404(Lavador, pk=pk)
    if request.method == 'POST':
        lavador.delete()
        messages.success(request, 'Lavador excluído com sucesso!')
        return redirect('lavador_list')
    return render(request, 'clientes/lavador_confirm_delete.html', {'lavador': lavador})

