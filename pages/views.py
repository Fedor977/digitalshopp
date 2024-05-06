from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import ReviewForm
from .models import Category, Product, Review, CartProduct, ForumPost, Cart, Account, Favorite, Reply


def index(request):
    categories = Category.objects.all()  # забираем все объекты из модели Category
    products = Product.objects.all()  # забираем все объекты из модели Product
    context = {
        'categories': categories,
        'products': products
    }
    return render(request, 'pages/index.html', context)


def get_categories(request, category_id):
    category = Category.objects.get(pk=category_id)

    context = {
        'category': category
    }

    return render(request, 'pages/index.html', context)


def search(request):  # определяем представление search, которое будет обрабатывать запросы поиска
    query = request.GET.get('q')  # в переменную query передаем GET запрос, используем метод get чтобы найти 'q'
    products = Product.objects.filter(name__icontains=query)  # фильтруем объекты Product по полю name

    # передаем в контекст продукты
    context = {
        'products': products
    }
    return render(request, 'pages/search.html', context)  # передаем контекст в шаблон


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'pages/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'pages/registration.html', {'form': form})


from django.contrib.auth.decorators import login_required


@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(pk=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_product, cart_product_created = CartProduct.objects.get_or_create(cart=cart, product=product)
        if not cart_product_created:
            cart_product.quantity += 1
            cart_product.save()
        return redirect('cart')
    else:
        return redirect('index')


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)


@login_required
def add_to_favorites(request, product_id):
    """Добавление в избранное"""
    product = Product.objects.get(pk=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user)
    favorite.products.add(product)
    return redirect('favorites')


@login_required
def remove_from_favorites(request, product_id):
    """Удаление из избранного"""
    product = Product.objects.get(pk=product_id)
    favorite = Favorite.objects.get(user=request.user)
    favorite.products.remove(product)
    return redirect('favorites')


@login_required
def favorites(request):
    """Избранное"""
    favorite, created = Favorite.objects.get_or_create(user=request.user)
    favorites = favorite.products.all()
    return render(request, 'pages/favorites.html', {'favorites': favorites})


def add_review(request, product_id):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            product = Product.objects.get(pk=product_id)
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', product_id=product_id)
    else:
        form = ReviewForm()
    return render(request, 'review_form.html', {'form': form})


from django.db.models import Sum


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'pages/detail.html', {'product': product})


def cart(request):
    cart_items = CartProduct.objects.filter(cart=request.user.cart)
    total_price = cart_items.aggregate(total=(Sum('quantity') * Sum('product__price')))['total'] or 0
    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'pages/cart.html', context)


@login_required
def forum(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_post_id = request.POST.get('parent_post_id')  # Получаем id родительского поста
        parent_post = ForumPost.objects.get(id=parent_post_id)  # Получаем объект родительского поста
        Reply.objects.create(user=request.user, content=content, parent_post=parent_post)
        return redirect('forum')
    else:
        posts = ForumPost.objects.filter(parent_post=None).order_by('-created_at')  # Сортировка по убыванию времени создания
        return render(request, 'pages/forum.html', {'posts': posts})



@login_required
def like_post(request, post_id):
    post = ForumPost.objects.get(id=post_id)  # обращаемся к id поста
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        post.dislikes.remove(request.user)  # удаляем дизлайк, если пользователь поставил лайк
    return JsonResponse({'like_count': post.like_count, 'dislike_count': post.dislike_count})


@login_required
def dislike_post(request, post_id):
    posts = ForumPost.objects.get(id=post_id)  # обращаемся к id поста
    if request.user in posts.dislikes.all():
        posts.dislikes.remove(request.user)
    else:
        posts.dislikes.add(request.user)
        posts.likes.remove(request.user)  # удаляем лайк, если пользователь поставил дизлайк
    return JsonResponse({'like_count': posts.like_count, 'dislike_count': posts.dislike_count})


@login_required
def reply_to_post(request, post_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_post = ForumPost.objects.get(id=post_id)
        Reply.objects.create(user=request.user, content=content, parent_post=parent_post)
        return redirect('forum')
    else:
        # Если запрос не POST, можно добавить обработку этого случая или просто перенаправить пользователя на главную страницу или другую страницу
        return redirect('index')