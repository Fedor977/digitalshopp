from enum import IntEnum

from django.db import models
from django.contrib.auth.models import User


# class Reaction(IntEnum):
#     NoReaction = 0
#     Like = 1
#     Dislike = -1

class CardGallery(models.Model):
    """Галлерея"""
    image = models.ImageField(verbose_name='Галлерея', upload_to='photos/gallery', blank=True, null=True)
    title = models.CharField(max_length=100, verbose_name='Заголовок', null=True)
    description = models.TextField(max_length=200, verbose_name='Описание', null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Галлерея'
        verbose_name_plural = 'Галлерея'



class CaruselItems(models.Model):
    """Карусель"""
    image = models.ImageField(verbose_name='Фото_карусель', upload_to='photos/carusel', blank=True, null=True)
    title = models.CharField(max_length=100, verbose_name='Заголовок', null=True)
    description = models.TextField(max_length=200, verbose_name='Описание', null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Карусель'
        verbose_name_plural = 'Карусель'


class ForumPost(models.Model):
    """Форум"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000, verbose_name='Поле ввода')
    parent_post = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    # todo: Refactoring to use enum reaction
    likes = models.ManyToManyField(User, related_name='post_likes', verbose_name='Лайк')
    dislikes = models.ManyToManyField(User, related_name='post_dislikes', verbose_name='Дизлайк')
    created_at = models.DateTimeField(auto_now=True)  # Добавляем поле created_at для хранения времени создания

    def __str__(self):
        return f'{self.user.username} - {self.content[:50]}'

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def dislike_count(self):
        return self.dislikes.count()


class Reply(models.Model):
    """Ответы на сообщения в форуме"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000, verbose_name='Текст ответа')
    parent_post = models.ForeignKey('ForumPost', on_delete=models.CASCADE, related_name='replies')
    replied_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    likes = models.ManyToManyField(User, related_name='reply_likes', verbose_name='Лайк')
    dislikes = models.ManyToManyField(User, related_name='reply_dislikes', verbose_name='Дизлайк')
    created_at = models.DateTimeField(auto_now=True)

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def dislike_count(self):
        return self.dislikes.count()

    def __str__(self):
        return f'Ответ {self.user.username} на сообщение {self.parent_post.id}'

    class Meta:
        ordering = ['-created_at']  # Сортировка по убыванию времени создания


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')

    def __str__(self):
        return self.name


class Product(models.Model):
    photo = models.ImageField(verbose_name='Фото', upload_to='photos/product/', blank=True, null=True)
    name = models.CharField(max_length=100, verbose_name='Название продукта')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    description = models.TextField(max_length=600, verbose_name='Описание')

    def __str__(self):
        return self.name


# корзина
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='cart')
    products = models.ManyToManyField(Product, through='CartProduct')


# в корзине
class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')
    quantity = models.IntegerField(default=1, verbose_name='Количество')


# модель для избранного
class Favorite(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    products = models.ManyToManyField(Product, verbose_name='Продукты')

    def __str__(self):
        return f'Избранное пользователя {self.user.username}'


# вывод данных
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorites = models.ManyToManyField(Product)


# отзыв
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(max_length=600, verbose_name='Описание отзыва')

    def __str__(self):
        return f'{self.user}, {self.product}, {self.text}'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-pk']

