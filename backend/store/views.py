
# django.core.paginator for pagination of product list
from django.core.paginator import Paginator
# django.db.models.Q for complex queries (search functionality)
from django.db.models import Q
# django.shortcuts.get_object_or_404 for fetching a single product or returning a 404 error
from django.shortcuts import get_object_or_404, render

from .models import Category, Product

from django.views.decorators.cache import cache_page

from django.core.cache import cache

CACHE_TIMEOUT = 60 * 5

def get_catalog_version():
    return cache.get("store:catalog_version", 1)

def get_cached_categories():
    version = get_catalog_version()
    key     = f"store:categories:v{version}"
    return cache.get_or_set(
        key,
        lambda: list(Category.objects.filter(is_active=True)),
        CACHE_TIMEOUT,
    )

def get_cached_products(search_query="",category_slug=""):
    version = get_catalog_version()
    key  = (
            f"store:products:v{version}:"
            f"q:{search_query.strip().lower()}:"
            f"category:{category_slug.strip().lower()}"
          )
    def fetch_products():
        products = Product.objects.filter(
            is_active=True,
            category__is_active=True,
        ).select_related("category")
         # Filter products based on search query and category slug
            # name__icontains is used for case-insensitive search in the product name
            # description__icontains is used for case-insensitive search in the product description
            # sku__icontains is used for case-insensitive search in the product SKU
            # Q objects are used to combine multiple conditions with OR logic
            # difference between __icontains and __iexact is that __icontains performs a case-insensitive search for a substring within a field, while __iexact performs a case-insensitive search for an exact match of the entire field value. In this case, we want to find products that contain the search query in their name, description, or SKU, so we use __icontains. 
        
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(sku__icontains=search_query)
            )
         # category__slug is used to filter products based on the slug of the related category
        if category_slug:
            products = products.filter(category__slug=category_slug)
        return list(products)
    return cache.get_or_set(key, fetch_products, CACHE_TIMEOUT)



def home(request):
    products = get_cached_products()[:8]
    categories = get_cached_categories()

    return render(
        request,
        "store/home.html",
        {
            "products": products,
            "categories": categories,
        },
    )


def product_list(request):
   
    
    
    search_query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()

    products = get_cached_products(
        search_query=search_query,
        category_slug=category_slug,
    )
    paginator = Paginator(products, 8)
    page_obj = paginator.get_page(request.GET.get("page"))

    categories = Category.objects.filter(is_active=True)
    #debug_catalog_cache()
    return render(
        request,
        "store/product_list.html",
        {
            "page_obj": page_obj,
            "products": page_obj.object_list,
            "categories": categories,
            "search_query": search_query,
            "selected_category": category_slug,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        slug=slug,
        is_active=True,
        category__is_active=True,
    )

    return render(
        request,
        "store/product_detail.html",
        {"product": product},
    )

def debug_catalog_cache():
    version = cache.get("store:catalog_version", 1)

    key = (
        f"store:products:v{version}:"
        "q::category:"
    )

    print("Catalog version:", version)
    print("Cache key:", key)
    print("Cached products:", cache.get(key))