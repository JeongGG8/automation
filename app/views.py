from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.utils import timezone

from .models import Role, Menu, RoleMenu, User
from .forms import RoleCreateForm, RoleEditForm, UserCreateForm, UserEditForm, MenuForm


def _get_menu_tree():
    root_menus = Menu.objects.filter(parent=None).prefetch_related('children')
    return root_menus


def _save_role_menus(role, menu_ids):
    RoleMenu.objects.filter(role=role).delete()
    for menu_id in menu_ids:
        RoleMenu.objects.create(role=role, menu_id=menu_id)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        return render(request, 'layouts/login.html', {'error': '아이디 또는 비밀번호가 올바르지 않습니다.'})
    return render(request, 'layouts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def index(request):
    return render(request, "index.html")


@login_required(login_url='login')
def role_list(request):
    roles = Role.objects.all().order_by('-id')
    return render(request, 'roles/list.html', {'roles': roles})


@login_required(login_url='login')
def role_create(request):
    if request.method == 'POST':
        form = RoleCreateForm(request.POST)
        if form.is_valid():
            now = timezone.now()
            role = form.save(commit=False)
            role.created_at = now
            role.created_by = request.user
            role.updated_at = now
            role.updated_by = request.user
            role.save()
            menu_ids = request.POST.getlist('menus')
            _save_role_menus(role, menu_ids)
            return redirect('role_list')
    else:
        form = RoleCreateForm()
    return render(request, 'roles/form.html', {
        'form': form,
        'action': '추가',
        'menu_tree': _get_menu_tree(),
        'checked_menu_ids': [],
    })


@login_required(login_url='login')
def role_edit(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        form = RoleEditForm(request.POST, instance=role)
        if form.is_valid():
            role = form.save(commit=False)
            role.updated_at = timezone.now()
            role.updated_by = request.user
            role.save()
            menu_ids = request.POST.getlist('menus')
            _save_role_menus(role, menu_ids)
            return redirect('role_list')
    else:
        form = RoleEditForm(instance=role)
    checked_menu_ids = list(RoleMenu.objects.filter(role=role).values_list('menu_id', flat=True))
    return render(request, 'roles/form.html', {
        'form': form,
        'action': '수정',
        'role': role,
        'menu_tree': _get_menu_tree(),
        'checked_menu_ids': checked_menu_ids,
    })


@login_required(login_url='login')
def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        try:
            role.delete()
        except ProtectedError:
            roles = Role.objects.all().order_by('id')
            return render(request, 'roles/list.html', {
                'roles': roles,
                'error': f'"{role.name}" 권한을 사용 중인 유저가 있어 삭제할 수 없습니다.',
            })
    return redirect('role_list')


@login_required(login_url='login')
def user_list(request):
    users = User.objects.select_related('role').order_by('-date_joined')
    return render(request, 'users/list.html', {'users': users})


@login_required(login_url='login')
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserCreateForm()
    return render(request, 'users/form.html', {
        'form': form,
        'action': '추가',
    })


@login_required(login_url='login')
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'users/form.html', {
        'form': form,
        'action': '수정',
        'target_user': user,
    })


@login_required(login_url='login')
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        try:
            user.delete()
        except ProtectedError:
            users = User.objects.select_related('role').order_by('-date_joined')
            return render(request, 'users/list.html', {
                'users': users,
                'error': f'"{user.username}" 유저를 삭제할 수 없습니다.',
            })
    return redirect('user_list')


def _get_full_menu_tree():
    return Menu.objects.filter(parent=None).prefetch_related('children').order_by('id')


@login_required(login_url='login')
def menu_list(request):
    return render(request, 'menus/list.html', {
        'menu_tree': _get_full_menu_tree(),
    })


@login_required(login_url='login')
def menu_create(request):
    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            menu = form.save()
            return redirect('menu_edit', pk=menu.pk)
    else:
        form = MenuForm()
    return render(request, 'menus/list.html', {
        'menu_tree': _get_full_menu_tree(),
        'form': form,
        'action': '추가',
    })


@login_required(login_url='login')
def menu_edit(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            return redirect('menu_edit', pk=menu.pk)
    else:
        form = MenuForm(instance=menu)
    return render(request, 'menus/list.html', {
        'menu_tree': _get_full_menu_tree(),
        'form': form,
        'action': '수정',
        'selected_menu': menu,
    })


@login_required(login_url='login')
def menu_delete(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    if request.method == 'POST':
        menu.delete()
    return redirect('menu_list')
