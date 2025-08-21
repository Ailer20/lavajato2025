from rest_framework import serializers
from .models import Lavagem
from clientes.models import Cliente, Veiculo, Lavador


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ["id", "nome", "cpf_cnpj", "telefone", "email", "endereco"]


class VeiculoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source="cliente.nome", read_only=True)

    class Meta:
        model = Veiculo
        fields = ["id", "placa", "marca", "modelo", "ano", "cor", "tipo", "cliente", "cliente_nome"]


class LavadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lavador
        fields = ["id", "nome", "cpf", "telefone", "data_admissao", "salario"]


class LavagemListSerializer(serializers.ModelSerializer):
    lavador_nome = serializers.CharField(source="lavador.nome", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    duracao_formatada = serializers.SerializerMethodField()

    class Meta:
        model = Lavagem
        fields = [
            "id", "codigo", "placa_veiculo", "hora_inicio", "hora_termino",
            "data_lavagem", "status", "status_display", "valor_servico", "valor_final",
            "base", "local", "tipo_lavagem", "transporte_equipamento",
            "lavador_nome", "duracao_formatada", "observacoes"
        ]

    def get_duracao_formatada(self, obj):
        if obj.duracao_lavagem:
            return f"{obj.duracao_lavagem} min"
        return None


class LavagemDetailSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    veiculo = VeiculoSerializer(read_only=True)
    lavador = LavadorSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    duracao_formatada = serializers.SerializerMethodField()

    class Meta:
        model = Lavagem
        fields = [
            "id", "codigo", "placa_veiculo", "hora_inicio", "hora_termino",
            "data_lavagem", "status", "status_display", "valor_servico", "valor_final",
            "base", "local", "tipo_lavagem", "transporte_equipamento",
            "cliente", "veiculo", "lavador", "observacoes", "duracao_formatada",
            "created_at", "updated_at"
        ]

    def get_duracao_formatada(self, obj):
        if obj.duracao_lavagem:
            return f"{obj.duracao_lavagem} min"
        return None


class LavagemCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lavagem
        fields = [
            "placa_veiculo", "base", "local", "tipo_lavagem",
            "transporte_equipamento", "lavador", "hora_inicio",
            "hora_termino", "data_lavagem", "observacoes"
        ]

    def validate_placa_veiculo(self, value):
        import re
        if not re.match(r"^[A-Z]{3}-?\d{4}$", value.upper()):
            raise serializers.ValidationError("Formato de placa inválido. Use ABC-1234 ou ABC1234.")
        return value.upper()

    def validate(self, data):
        if data.get("hora_termino") and data.get("hora_inicio"):
            if data["hora_termino"] <= data["hora_inicio"]:
                raise serializers.ValidationError("Hora de término deve ser posterior à hora de início.")
        return data


class EstatisticasSerializer(serializers.Serializer):
    total_lavagens = serializers.IntegerField()
    lavagens_em_andamento = serializers.IntegerField()
    lavagens_concluidas = serializers.IntegerField()
    lavagens_canceladas = serializers.IntegerField()
    faturamento_mes = serializers.DecimalField(max_digits=10, decimal_places=2)
    faturamento_dia = serializers.DecimalField(max_digits=10, decimal_places=2)
    tempo_medio_lavagem = serializers.IntegerField()
    lavagens_por_status = serializers.DictField()


