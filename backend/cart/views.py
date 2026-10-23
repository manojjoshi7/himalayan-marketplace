
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from store.models import Product
from .cart import Cart


def cart_detail(request):
    cart = Cart(request)

    return render(
        request,
        "cart/cart_detail.html",
        {
            "cart": cart,
            "cart_items": list(cart),
            "subtotal": cart.get_subtotal(),
        },
    )


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        id=product_id,
        is_active=True,
        category__is_active=True,
    )

    try:
        quantity = int(request.POST.get("quantity", 1))

        if quantity < 1:
            raise ValueError

        cart = Cart(request)
        cart.add(product, quantity=quantity)

        messages.success(
            request,
            f"{product.name} added to your cart.",
        )
    except ValueError:
        messages.error(
            request,
            "Please enter a valid quantity and check product availability.",
        )

    return redirect("cart:cart_detail")


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
        category__is_active=True,
    )

    try:
        quantity = int(request.POST.get("quantity", 1))

        if quantity < 1:
            raise ValueError

        cart = Cart(request)
        cart.add(
            product,
            quantity=quantity,
            override_quantity=True,
        )

        messages.success(request, "Cart quantity updated.")
    except ValueError as error:
        messages.error(request, str(error) or "Invalid quantity.")

    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    cart.remove(product)
    messages.success(request, "Product removed from your cart.")

    return redirect("cart:cart_detail")
