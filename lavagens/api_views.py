from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Lavagem
from .serializers import (
    LavagemListSerializer, LavagemDetailSerializer, 
    LavagemCreateUpdateSerializer, EstatisticasSerializer
)


class LavagemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar lavagens
    """
    queryset = Lavagem.objects.all().select_related(
        'cliente', 'veiculo', 'lavador'
    ).order_by("-data_lavagem")
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'tipo_lavagem', 'transporte_equipamento']
    search_fields = ['codigo', 'placa_veiculo', 'cliente__nome', 'lavador__nome']
    ordering_fields = ['created_at', 'hora_inicio', 'hora_termino', 'valor_final']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LavagemListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return LavagemCreateUpdateSerializer
        else:
            return LavagemDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')
        
        if data_inicio:
            queryset = queryset.filter(data_lavagem__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_lavagem__lte=data_fim)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def concluir(self, request, pk=None):
        """Concluir uma lavagem"""
        lavagem = self.get_object()
        
        if lavagem.status != 'EM_ANDAMENTO':
            return Response(
                {'error': 'Apenas lavagens em andamento podem ser concluídas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lavagem.concluir_lavagem()
        
        return Response({
            'message': 'Lavagem concluída com sucesso',
            'lavagem': LavagemDetailSerializer(lavagem).data
        })
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar uma lavagem"""
        lavagem = self.get_object()
        motivo = request.data.get('motivo', '')
        
        if lavagem.status != 'EM_ANDAMENTO':
            return Response(
                {'error': 'Apenas lavagens em andamento podem ser canceladas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lavagem.cancelar_lavagem(motivo)
        
        return Response({
            'message': 'Lavagem cancelada com sucesso',
            'lavagem': LavagemDetailSerializer(lavagem).data
        })
    
    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Obter estatísticas das lavagens"""
        hoje = timezone.now().date()
        inicio_mes = hoje.replace(day=1)
        
        total_lavagens = Lavagem.objects.count()
        lavagens_em_andamento = Lavagem.objects.filter(status='EM_ANDAMENTO').count()
        lavagens_concluidas = Lavagem.objects.filter(status='CONCLUIDA').count()
        lavagens_canceladas = Lavagem.objects.filter(status='CANCELADA').count()
        
        faturamento_mes = Lavagem.objects.filter(
            status='CONCLUIDA',
            data_lavagem__gte=inicio_mes
        ).aggregate(total=Sum('valor_final'))['total'] or Decimal('0.00')
        
        faturamento_dia = Lavagem.objects.filter(
            status='CONCLUIDA',
            data_lavagem=hoje
        ).aggregate(total=Sum('valor_final'))['total'] or Decimal('0.00')
        
        tempo_medio = Lavagem.objects.filter(
            status='CONCLUIDA',
            duracao_lavagem__isnull=False
        ).aggregate(media=Avg('duracao_lavagem'))['media'] or 0
        
        lavagens_por_status = dict(
            Lavagem.objects.values('status')
            .annotate(total=Count('id'))
            .values_list('status', 'total')
        )
        
        estatisticas = {
            'total_lavagens': total_lavagens,
            'lavagens_em_andamento': lavagens_em_andamento,
            'lavagens_concluidas': lavagens_concluidas,
            'lavagens_canceladas': lavagens_canceladas,
            'faturamento_mes': faturamento_mes,
            'faturamento_dia': faturamento_dia,
            'tempo_medio_lavagem': int(tempo_medio),
            'lavagens_por_status': lavagens_por_status,
        }
        
        serializer = EstatisticasSerializer(estatisticas)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def relatorio_periodo(self, request):
        """Relatório de lavagens por período"""
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')
        
        if not data_inicio or not data_fim:
            return Response(
                {'error': 'Parâmetros data_inicio e data_fim são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de data inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lavagens = Lavagem.objects.filter(
            data_lavagem__range=[data_inicio, data_fim]
        ).select_related(
            'cliente', 'veiculo', 'lavador'
        )
        
        total_periodo = lavagens.count()
        concluidas_periodo = lavagens.filter(status='CONCLUIDA').count()
        faturamento_periodo = lavagens.filter(status='CONCLUIDA').aggregate(
            total=Sum('valor_final')
        )['total'] or Decimal('0.00')
        
        serializer = LavagemListSerializer(lavagens, many=True)
        
        return Response({
            'periodo': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'total_lavagens': total_periodo,
                'lavagens_concluidas': concluidas_periodo,
                'faturamento_total': faturamento_periodo
            },
            'lavagens': serializer.data
        })


