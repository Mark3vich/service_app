from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from services.serializers import SubscriptionSerializer
from services.models import Subscription
from django.db.models import Prefetch
from clients.models import Client
from django.db.models import F, Sum

# Create your views here.
class SubscriptionView(ReadOnlyModelViewSet):
    # prefetch_related сэкономит запросы к бд и соответсаенно оптимизирует работу программы. Проблема n + 1 - решена 
    queryset = Subscription.objects.all().prefetch_related(
        'plan',
        Prefetch('client', queryset=Client.objects.all().select_related('user').only('company_name', 'user__email'))
        )
    serializer_class = SubscriptionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)

        response_data = {'result': response.data}
        response_data['total'] = queryset.aggregate(total=Sum('price')).get('total')
        response.data = response_data

        return response