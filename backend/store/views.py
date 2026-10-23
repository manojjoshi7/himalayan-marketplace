
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.core.cache import cache

from .models import Category, Product


CACHE_TIMEOUT = 60 * 5
PRODUCTS_PER_PAGE = 8


def get_catalog_version():
    return cache.get("store:catalog_version", 1)


def get_cached_categories():
    version = get_catalog_version()
    key = f"store:categories:v{version}"

    return cache.get_or_set(
        key,
        lambda: list(
            Category.objects.filter(is_active=True)
        ),
        CACHE_TIMEOUT,
    )


def get_products_queryset(search_query="", category_slug=""):
    """
    Return a lazy QuerySet.
    PostgreSQL performs filtering and sorting.
    Products are not loaded into Python until evaluated.
    """
    products = Product.objects.filter(
        is_active=True,
        category__is_active=True,
    ).select_related("category").order_by("-created_at", "-id")

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(sku__icontains=search_query)
        )

    if category_slug:
        products = products.filter(
            category__slug=category_slug
        )

    return products


def get_cached_product_page(
    search_query="",
    category_slug="",
    page_number=1,
):
    """
    Cache only the products for one page, not the full catalog.
    """
    version = get_catalog_version()

    key = (
        f"store:products:v{version}:"
        f"q:{search_query.strip().lower()}:"
        f"category:{category_slug.strip().lower()}:"
        f"page:{page_number}:"
        f"per_page:{PRODUCTS_PER_PAGE}"
    )

    def fetch_page():
        products = get_products_queryset(
            search_query=search_query,
            category_slug=category_slug,
        )

        paginator = Paginator(products, PRODUCTS_PER_PAGE)
        page_obj = paginator.get_page(page_number)

        # Evaluate only this page's QuerySet.
        return list(page_obj.object_list)

    return cache.get_or_set(
        key,
        fetch_page,
        CACHE_TIMEOUT,
    )


def home(request):
    # Fetch at most 8 products from PostgreSQL on a cache miss.
    products = get_cached_product_page(page_number=1)
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

    # Use a lazy QuerySet so Django can paginate in PostgreSQL.
    products_queryset = get_products_queryset(
        search_query=search_query,
        category_slug=category_slug,
    )

    paginator = Paginator(
        products_queryset,
        PRODUCTS_PER_PAGE,
    )

    page_obj = paginator.get_page(request.GET.get("page"))

    # Cache the products for this page separately.
    cached_products = get_cached_product_page(
        search_query=search_query,
        category_slug=category_slug,
        page_number=page_obj.number,
    )

    categories = get_cached_categories()

    return render(
        request,
        "store/product_list.html",
        {
            "page_obj": page_obj,
            "products": cached_products,
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
    version = get_catalog_version()

    key = (
        f"store:products:v{version}:"
        "q::category::page:1:per_page:8"
    )

    print("Catalog version:", version)
    print("Cache key:", key)
    print("Cached products:", cache.get(key))
