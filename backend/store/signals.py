from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Category, Product

CATALOG_VERSION_KEY = "store:catalog_version"

def invalidate_catalog_cache():
    # Create the version key if it does not exist.
    if not cache.add(CATALOG_VERSION_KEY, 1, timeout=None):
        # Key already exists, so increase the version by 1.
        cache.incr(CATALOG_VERSION_KEY)

@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def catalog_changed(sender, **kwargs):
    invalidate_catalog_cache()
