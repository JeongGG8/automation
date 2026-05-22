from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Menu(models.Model):
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children'
    )
    name = models.CharField(max_length=50)
    url_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '메뉴'
        verbose_name_plural = '메뉴 목록'


class Role(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True)
    menus = models.ManyToManyField(Menu, through='RoleMenu', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    created_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_roles'
    )
    updated_at = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='updated_roles'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '권한'
        verbose_name_plural = '권한 목록'


class RoleMenu(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('role', 'menu')
        verbose_name = '권한-메뉴'
        verbose_name_plural = '권한-메뉴 목록'


class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=50, blank=True)
    # is_active는 AbstractUser에 이미 포함되어 있음
