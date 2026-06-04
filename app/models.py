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
    code = models.CharField(max_length=50, unique=True)
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


class UploadedFile(models.Model):
    FILE_TYPE_CHOICES = [
        ('transaction', '거래내역'),
        ('secretary', '서기파일'),
        ('other', '기타'),
    ]

    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.file_name

    class Meta:
        verbose_name = '업로드 파일'
        verbose_name_plural = '업로드 파일 목록'


class TransactionFile(models.Model):
    upload = models.OneToOneField(
        UploadedFile, on_delete=models.CASCADE,
        related_name='transaction_file'
    )
    name = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    period_start = models.DateField()
    period_end = models.DateField()
    bank_name = models.CharField(max_length=50)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '거래내역 파일'
        verbose_name_plural = '거래내역 파일 목록'


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('deposit', '입금'),
        ('withdrawal', '출금'),
    ]

    transaction_file = models.ForeignKey(
        TransactionFile, on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_at = models.DateTimeField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.PositiveIntegerField()
    balance = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    memo = models.CharField(max_length=200, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.transaction_at} {self.get_type_display()} {self.amount}'

    class Meta:
        verbose_name = '거래내역'
        verbose_name_plural = '거래내역 목록'
        ordering = ['-transaction_at']
