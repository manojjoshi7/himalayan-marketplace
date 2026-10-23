from decimal import Decimal

from store.models import Product

from .models import Cart as CartModel, CartItem

class Cart:

    def __init__(self, request):
        self.session = request.session
        self.user    = (request.user if request.user.is_authenticated else None)

        if self.user is None:
            cart = self.session.get('cart')
            if cart is None:
               cart = self.session['cart'] = {}
            self.cart = cart
        else:
            self.cart = None    
  
    def add(self, product: Product, quantity: int = 1,override_quantity=False):

        if self.user:
            db_cart, created   = CartModel.objects.get_or_create(user=self.user)
            item, created = CartItem.objects.get_or_create(cart=db_cart, product=product, defaults={'quantity': quantity})

            new_quantity = (quantity if override_quantity else item.quantity + quantity)

            if new_quantity < 1:
                raise ValueError("Quantity must be at least 1.")

            if new_quantity > product.stock:
                raise ValueError(f"Cannot add {new_quantity} items. Only {product.stock} in stock.")

            item.quantity = new_quantity
            item.save(update_fields=['quantity'])
            db_cart.save(update_fields=['updated_at'])
            return

        product_id = str(product.id)
        current_quantity = self.cart.get(product_id, 0)
        new_quantity = (quantity if override_quantity else current_quantity + quantity)

        if new_quantity < 1:
            raise ValueError("Quantity must be at least 1.")
        if new_quantity > product.stock:
            raise ValueError(f"Cannot add {new_quantity} items. Only {product.stock} in stock.")

        self.cart[product_id] = new_quantity
        self.save()

    def remove(self, product):

        if self.user:
            CartItem.objects.filter(
                cart__user=self.user,
                product=product,
            ).delete()
            return

        self.cart.pop(str(product.id), None)
        self.save()

    def save(self):
        if self.user is None:
            self.session["cart"] = self.cart
            self.session.modified = True 

    def __len__(self):
        if self.user:
            db_cart = CartModel.objects.filter(
                user=self.user
            ).first()

            if db_cart is None:
                return 0

            return sum(
                item.quantity
                for item in db_cart.items.all()
            )

        return sum(int(quantity) for quantity in self.cart.values())        

    def get_subtotal(self):
        return sum(
              (item["total_price"] for item in self),
              Decimal("0.00"),
         )

    def __iter__(self):

        # Case 1: Logged-in user — get cart items from database
        if self.user:

            db_cart = CartModel.objects.filter(
                user=self.user
            ).first()

            if db_cart is None:
                return

            cart_items = CartItem.objects.filter(
                cart=db_cart,
                product__is_active=True,
                product__category__is_active=True,
            ).select_related(
                "product",
                "product__category",
            )

            for item in cart_items:
                product = item.product
                quantity = item.quantity
                price = product.price

                yield {
                    "product": product,
                    "quantity": quantity,
                    "price": price,
                    "total_price": price * quantity,
                }

            return

        # Case 2: Guest user — get cart items from session
        product_ids = self.cart.keys()

        products = Product.objects.filter(
            id__in=product_ids,
            is_active=True,
            category__is_active=True,
        ).select_related("category")

        products_by_id = {
            str(product.id): product
            for product in products
        }

        for product_id in list(self.cart.keys()):

            product = products_by_id.get(product_id)

            # Remove deleted or inactive products from guest cart
            if product is None:
                del self.cart[product_id]
                self.save()
                continue

            quantity = int(self.cart[product_id])
            price = product.price

            yield {
                "product": product,
                "quantity": quantity,
                "price": price,
                "total_price": price * quantity,
            }
    
def merge_session_cart(request):
        """ Merge guest session items into the logged-in user's cart. """
        if not request.user.is_authenticated:
            return

        session_cart = request.session.get('cart', {})

        if not session_cart:
            return

        cart = Cart(request)

        for product_id, guest_quantity in session_cart.items():
            try:
                 # category__is_active is used to ensure that the product belongs to an active category. This is important because even if a product is active, it might belong to a category that has been deactivated. By checking both the product's active status and its category's active status, we ensure that only valid products are merged into the user's cart.
                 product = Product.objects.get(
                        id = int(product_id),
                        is_active=True,
                        category__is_active=True

                    )
                 guest_quantity = int(guest_quantity)

            except (Product.DoesNotExist, ValueError,TypeError):
                   continue

            if guest_quantity < 1 or product.stock < 1:
               continue 
            # _ means we are ignoring the second value returned by get_or_create, which indicates whether a new object was created or an existing one was retrieved. In this context, we only care about the Cart instance itself, so we use _ to ignore the boolean value.
            db_cart, _ = CartModel.objects.get_or_create(
            user = request.user
           )

            existing_item = CartItem.objects.filter(
                cart=db_cart,
                product=product,
            ).first()

            existing_quantity = (
                existing_item.quantity if existing_item else 0
            )
            combined_quantity = min(
                existing_quantity + guest_quantity,
                product.stock,
            )

            try:
                cart.add(
                    product,
                    quantity=combined_quantity,
                    override_quantity=True,
                )
            except ValueError:
                continue

       # Remove guest data after processing the merge.
        request.session.pop("cart", None)
        request.session.modified = True      

     