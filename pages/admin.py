from django.contrib import admin
from .models import Category, Product, Review, Cart, CartProduct, ForumPost, Favorite, Reply, CaruselItems, CardGallery

admin.site.register(ForumPost)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Favorite)
admin.site.register(Reply)
admin.site.register(CaruselItems)
admin.site.register(CardGallery)
