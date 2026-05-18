from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.utils import timezone

from .models import Role
from .forms import RoleForm


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
    roles = Role.objects.all().order_by('id')
    return render(request, 'roles/list.html', {'roles': roles})


@login_required(login_url='login')
def role_create(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            now = timezone.now()
            role = form.save(commit=False)
            role.created_at = now
            role.created_by = request.user
            role.updated_at = now
            role.updated_by = request.user
            role.save()
            return redirect('role_list')
    else:
        form = RoleForm()
    return render(request, 'roles/form.html', {'form': form, 'action': '추가'})


@login_required(login_url='login')
def role_edit(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            role = form.save(commit=False)
            role.updated_at = timezone.now()
            role.updated_by = request.user
            role.save()
            return redirect('role_list')
    else:
        form = RoleForm(instance=role)
    return render(request, 'roles/form.html', {'form': form, 'action': '수정'})


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
