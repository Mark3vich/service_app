from django.conf import settings
from rest_framework.viewsets import ReadOnlyModelViewSet
from services.serializers import SubscriptionSerializer
from services.models import Subscription
from django.db.models import Prefetch
from clients.models import Client
from django.db.models import Sum
from django.core.cache import cache

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

        price_cache = cache.get(settings.PRICE_CACHE_NAME)
        if price_cache:
            total_price = price_cache
        else: 
            total_price = queryset.aggregate(total=Sum('price')).get('total')
            cache.set(settings.PRICE_CACHE_NAME, total_price, 60*60*24)

        response_data = {'result': response.data}
        response_data['total'] = total_price
        response.data = response_data

        return response