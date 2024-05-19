from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from .forms import ReviewForm
from .models import Category, Product, Review, CartProduct, ForumPost, Cart, Favorite, Reply, CaruselItems, \
    CardGallery


def get_common_context(request, category_id=None):
    categories = Category.objects.all()
    carusel_items = CaruselItems.objects.all()

    if category_id:
        category = get_object_or_404(Category, pk=category_id)
        products = Product.objects.filter(category=category)
    else:
        category = None
        products = Product.objects.all()

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'carusel_items': carusel_items,
        'page_obj': page_obj,
        'category': category,
    }

    return context


def index(request):
    context = get_common_context(request)
    return render(request, 'pages/index.html', context)


def get_categories(request, category_id):
    context = get_common_context(request, category_id)
    return render(request, 'pages/index.html', context)


def about(request):
    carusel_items = CaruselItems.objects.all()
    gallery = CardGallery.objects.all()
    categories = Category.objects.all()
    context = {
        'carusel_items': carusel_items,
        'gallery': gallery,
        'categories': categories,
    }
    return render(request, 'pages/about.html', context)

def search(request):  # определяем представление search, которое будет обрабатывать запросы поиска
    query = request.GET.get('q')  # в переменную query передаем GET запрос, используем метод get чтобы найти 'q'
    products = Product.objects.filter(Q(name__icontains=query) | Q(
        name__icontains=query.capitalize()))  # фильтруем объекты Product по полю name. Второй код ищет название по верхнему регистру

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


def cart(request):
    cart_items = CartProduct.objects.filter(cart=request.user.cart)
    total_price = cart_items.aggregate(total=(Sum('quantity') * Sum('product__price')))['total'] or 0
    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'pages/cart.html', context)


@login_required
def add_to_favorites(request, product_id):
    """Добавление в избранное"""
    product = Product.objects.get(pk=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user)
    favorite.products.add(product)
    favorite.save()
    return redirect('favorites')


@login_required
def remove_from_favorites(request, product_id):
    """Удаление из избранного"""
    product = Product.objects.get(pk=product_id)
    favorite = Favorite.objects.get(user=request.user)
    favorite.products.remove(product)
    favorite.save()
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
    return render(request, 'pages/add_review.html', {'form': form})


from django.db.models import Sum, Q


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    reviews = Review.objects.filter(product=product)
    print(reviews)

    context = {
        'product': product,
        'reviews': reviews
    }

    return render(request, 'pages/detail.html', context)



from django.core.paginator import Paginator


def forum(request):
    if request.method == 'POST':
        # Обработка создания нового сообщения
        content = request.POST.get('content')
        parent_post_id = request.POST.get('parent_post_id')
        if parent_post_id:
            parent_post = get_object_or_404(ForumPost, id=parent_post_id)
            Reply.objects.create(user=request.user, content=content, parent_post=parent_post)
        else:
            ForumPost.objects.create(user=request.user, content=content)
        return redirect('forum')
    else:
        try:
            all_post_ids = ForumPost.objects.filter(parent_post=None).order_by('-created_at').values_list('id', flat=True) # получение списка всех ID постов на форуме

            # разбиение списка ID постов на страницы по 10 ID каждая
            paginator = Paginator(all_post_ids, 10)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)

            posts = ForumPost.objects.filter(id__in=page_obj.object_list).order_by('-created_at') # получение соответствующих постов для текущей страницы

        except Exception as e:
            # обработка исключений
            print(f"An error occurred: {e}")
            page_obj = None
            posts = None

        context = {
            'posts': posts,
            'page_obj': page_obj
        }

        return render(request, 'pages/forum.html', context)



@login_required
def like_post(request, post_id):
    post = ForumPost.objects.get(id=post_id)  # обращаемся к id поста
    try:
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
            post.dislikes.remove(request.user)  # удаляем дизлайк, если пользователь поставил лайк
    except Exception as e:
        print(e)
    return redirect('forum')


@login_required
def dislike_post(request, post_id):
    posts = ForumPost.objects.get(id=post_id)  # обращаемся к id поста
    try:
        if request.user in posts.dislikes.all():
            posts.dislikes.remove(request.user)
        else:
            posts.dislikes.add(request.user)
            posts.likes.remove(request.user)  # удаляем лайк, если пользователь поставил дизлайк
    except Exception as e:
        print(e)
    return redirect('forum')


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    if request.user == post.user:
        post.delete()
    return redirect('forum')


@login_required
def reply_to_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        replied_to_id = request.POST.get('replied_to_id')

        replied_to = None
        if replied_to_id:
            replied_to = get_object_or_404(Reply, id=replied_to_id)

        Reply.objects.create(user=request.user, content=content, parent_post=post, replied_to=replied_to)
        return redirect('forum')
    else:
        replies = post.replies.all().order_by('-created_at')
        return render(request, 'pages/forum.html', {'post': post, 'replies': replies})


@login_required
def like_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    try:
        if request.user in reply.likes.all():
            reply.likes.remove(request.user)
        else:
            reply.likes.add(request.user)
            reply.dislikes.remove(request.user)
    except Exception as e:
        print(e)
    return redirect('forum')


@login_required
def dislike_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    try:
        if request.user in reply.dislikes.all():
            reply.dislikes.remove(request.user)
        else:
            reply.dislikes.add(request.user)
            reply.likes.remove(request.user)
    except Exception as e:
        print(e)
    return redirect('forum')


@login_required
def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    if request.user == reply.user:
        reply.delete()
    return redirect('forum')
