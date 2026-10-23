from django.db import models
from django.conf import settings

class Cart(models.Model):
    
    user  = models.OneToOneField(settings.AUTH_USER_MODEL, 
                                on_delete=models.CASCADE,
                                related_name='shopping_cart')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):

    cart = models.ForeignKey(Cart, 
                             on_delete=models.CASCADE, 
                             related_name='items')
    
    product = models.ForeignKey('store.Product', 
                                on_delete=models.CASCADE)
    
    quantity = models.PositiveIntegerField(default=1)
    # Meta class to enforce unique constraint on cart and product combination
    # We want to ensure that a user cannot have multiple entries of the same product in their cart.
    # Why Meta class is used here: The Meta class in Django models is used to define metadata for the model. In this case, we are using it to enforce a unique constraint on the combination of cart and product fields. This ensures that each product can only appear once in a user's cart, preventing duplicate entries.
    # Other information: The unique_together constraint is a way to enforce that a combination of fields must be unique across the database. In this case, it ensures that for each cart, a specific product can only appear once. This is important for maintaining data integrity and providing a better user experience, as it prevents users from accidentally adding the same product multiple times to their cart. 
    class Meta:
    
        #unique_together = ('cart', 'product')
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product'], name='unique_cart_item')
        ]


    def __str__(self):
        return f"{self.quantity} of {self.product.name} in cart for {self.cart.user.username}"
     