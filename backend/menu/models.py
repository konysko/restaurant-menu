from django.db import models


class Menu(models.Model):
    name = models.CharField(max_length=1024, unique=True)
    description = models.TextField()

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Menu {self.name}'


class Dish(models.Model):
    name = models.CharField(max_length=1024, unique=True)
    description = models.TextField()

    price = models.DecimalField(max_digits=4, decimal_places=2)
    prepare_time = models.DurationField()
    is_vegetarian = models.BooleanField()
    picture = models.ImageField(blank=True)

    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='dishes'
    )

    def __str__(self) -> str:
        return f'Dish {self.name} in menu {self.menu}'
