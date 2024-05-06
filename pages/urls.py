from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('', views.home, name='home'),
    # path('forum/', views.forum),
    path('add_to_favorites/<int:product_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('remove_from_favorites/<int:product_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('favorites/', views.favorites, name='favorites'),
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('registration/', views.registration, name='registration'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    # path('login', views.user_login, name='login'),
    path('logout/', views.logout, name='logout'),
    # path('add_review/', views.add_review, name='add_review'),
    path('forum/', views.forum, name='forum'),
    path('forum/reply', views.reply_to_post, name='reply_to_post'),
    # path('reply/<int:post_id>/', views.reply_to_post, name='reply_to_post'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('dislike/<int:post_id>/', views.dislike_post, name='dislike_post'),
    path('cart/', views.cart, name='cart'),
    # path('add_to_cart', views.add_to_cart, name='add_to_cart'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>add_review/', views.add_review, name='add_review'),
    path('login/', views.user_login, name='login'),
    path('category/<int:category_id>/', views.get_categories, name='category'),
]
