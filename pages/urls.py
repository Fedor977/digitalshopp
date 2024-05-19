from django.urls import path
from . import views

urlpatterns = [
    path('add_to_favorites/<int:product_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('remove_from_favorites/<int:product_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('favorites/', views.favorites, name='favorites'),
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('registration/', views.registration, name='registration'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('logout/', views.user_logout, name='logout'),
    path('forum/', views.forum, name='forum'),
    path('forum/<int:post_id>/delete', views.delete_post, name='delete_post'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('dislike/<int:post_id>/', views.dislike_post, name='dislike_post'),
    path('cart/', views.cart, name='cart'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>add_review/', views.add_review, name='add_review'),
    path('login/', views.user_login, name='login'),
    path('category/<int:category_id>/', views.get_categories, name='category'),
    path('forum/reply/<int:post_id>/', views.reply_to_post, name='reply_to_post'),
    path('like/reply/<int:reply_id>/', views.like_reply, name='like_reply'),
    path('dislike/reply/<int:reply_id>/', views.dislike_reply, name='dislike_reply'),
    path('delete/reply/<int:reply_id>', views.delete_reply, name='delete_reply'),
    path('about/', views.about, name='about')
]
