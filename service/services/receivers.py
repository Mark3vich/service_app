from django.core.cache import cache
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_delete

@receiver(post_delete, sender=None)
def delete_cache_totlal_sum(*args, **kwargs):
    cache.delete(settings.PRICE_CACHE_NAME)
