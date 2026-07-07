import os
import uuid
import openpyxl
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError, Count, Q, Sum, Min, Max, Prefetch
from django.utils import timezone
from django.conf import settings

from .models import Role, Menu, RoleMenu, User, TransactionLedger, TransactionUpload, UploadedFile, Transaction, Receipt
from .forms import RoleCreateForm, RoleEditForm, UserCreateForm, UserEditForm, MenuForm, TransactionUploadForm


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


@login_required(login_url='login')
def transaction_list(request):
    ledgers = (
        TransactionLedger.objects
        .annotate(
            total_deposit=Sum('transactions__amount', filter=Q(transactions__is_deleted=False, transactions__type='deposit')),
            total_withdrawal=Sum('transactions__amount', filter=Q(transactions__is_deleted=False, transactions__type='withdrawal')),
        )
        .order_by('-year')
    )

    years_data = []
    for ledger in ledgers:
        uploads = (
            ledger.uploads
            .filter(is_deleted=False)
            .select_related('upload')
            .annotate(
                transaction_count=Count('transactions', filter=Q(transactions__is_deleted=False)),
                upload_deposit=Sum('transactions__amount', filter=Q(transactions__is_deleted=False, transactions__type='deposit')),
                upload_withdrawal=Sum('transactions__amount', filter=Q(transactions__is_deleted=False, transactions__type='withdrawal')),
            )
            .order_by('-upload__uploaded_at')
        )
        deposit = ledger.total_deposit or 0
        withdrawal = ledger.total_withdrawal or 0
        missing_receipts = (
            ledger.transactions
            .filter(is_deleted=False, type='withdrawal')
            .exclude(receipts__is_deleted=False)
            .count()
        )
        years_data.append({
            'ledger': ledger,
            'uploads': uploads,
            'total_deposit': deposit,
            'total_withdrawal': withdrawal,
            'net': deposit - withdrawal,
            'missing_receipts': missing_receipts,
        })

    return render(request, 'transactions/list.html', {
        'years_data': years_data,
    })


def _parse_kakao_excel(file_path):
    wb = openpyxl.load_workbook(file_path, data_only=True, read_only=True)
    ws = wb.active
    transactions = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i < 11:
            continue
        _, date_str, type_str, amount_str, balance_str, trans_type, description, memo, *_ = row
        if not date_str or not type_str:
            continue
        try:
            transaction_at = timezone.make_aware(
                datetime.strptime(str(date_str).strip(), '%Y.%m.%d %H:%M:%S')
            )
            amount = int(str(amount_str).replace(',', '').replace('-', '').strip())
            balance = int(str(balance_str).replace(',', '').replace('-', '').strip())
            type_code = 'deposit' if str(type_str).strip() == '입금' else 'withdrawal'
            transactions.append({
                'transaction_at': transaction_at,
                'type': type_code,
                'amount': amount,
                'balance': balance,
                'transaction_type': str(trans_type).strip() if trans_type else '',
                'description': str(description).strip() if description else '',
                'memo': str(memo).strip() if memo else '',
            })
        except (ValueError, AttributeError):
            continue
    wb.close()
    return transactions


@login_required(login_url='login')
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            save_dir = os.path.join(settings.MEDIA_ROOT, 'transactions')
            os.makedirs(save_dir, exist_ok=True)
            file_path = os.path.join(save_dir, uploaded_file.name)
            with open(file_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            uploaded = UploadedFile.objects.create(
                file_name=uploaded_file.name,
                file_path=file_path,
                file_type='transaction',
                uploaded_by=request.user,
            )
            rows = _parse_kakao_excel(file_path)
            if not rows:
                uploaded.delete()
                form.add_error('file', '거래내역이 없는 파일입니다.')
                return render(request, 'transactions/form.html', {'form': form})
            dates = [r['transaction_at'].date() for r in rows]
            ledger, _ = TransactionLedger.objects.get_or_create(
                year=form.cleaned_data['year'],
                defaults={'bank_name': form.cleaned_data['bank_name']},
            )
            tu = TransactionUpload.objects.create(
                ledger=ledger,
                upload=uploaded,
                name=form.cleaned_data['name'],
                period_start=min(dates),
                period_end=max(dates),
            )
            # 원장에 이미 있는 거래는 건너뛰고 새 거래만 삽입 (기존 메모 보존)
            # 삭제된 거래와 일치하면 복구하고 이번 업로드 소속으로 변경
            existing = {}
            for t in ledger.transactions.values('id', 'transaction_at', 'type', 'amount', 'balance', 'is_deleted'):
                existing[(t['transaction_at'], t['type'], t['amount'], t['balance'])] = t
            new_transactions = []
            restore_ids = []
            for row in rows:
                key = (row['transaction_at'], row['type'], row['amount'], row['balance'])
                found = existing.get(key)
                if found:
                    if found['is_deleted']:
                        restore_ids.append(found['id'])
                        found['is_deleted'] = False
                    continue
                existing[key] = {'id': None, 'is_deleted': False}
                new_transactions.append(Transaction(ledger=ledger, source_upload=tu, **row))
            Transaction.objects.bulk_create(new_transactions)
            if restore_ids:
                Transaction.objects.filter(id__in=restore_ids).update(
                    is_deleted=False, source_upload=tu
                )
            return redirect('transaction_list')
    else:
        form = TransactionUploadForm()
    return render(request, 'transactions/form.html', {'form': form})


@login_required(login_url='login')
def transaction_memo_update(request, pk):
    from django.http import JsonResponse
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.memo = request.POST.get('memo', '').strip()
        transaction.save()
        return JsonResponse({'ok': True, 'memo': transaction.memo})
    return JsonResponse({'ok': False}, status=405)


@login_required(login_url='login')
def transaction_delete(request, pk):
    tu = get_object_or_404(TransactionUpload, pk=pk)
    if request.method == 'POST':
        tu.is_deleted = True
        tu.save()
        tu.transactions.update(is_deleted=True)
    return redirect('transaction_list')


@login_required(login_url='login')
def transaction_detail(request, pk):
    ledger = get_object_or_404(TransactionLedger, pk=pk)
    type_filter = request.GET.get('type', '')
    search_field = request.GET.get('search_field', 'description')
    search = request.GET.get('search', '').strip()
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    all_transactions = (
        ledger.transactions.filter(is_deleted=False)
        .order_by('transaction_at')
        .prefetch_related(Prefetch(
            'receipts',
            queryset=Receipt.objects.filter(is_deleted=False),
            to_attr='active_receipts',
        ))
    )
    period = all_transactions.aggregate(start=Min('transaction_at'), end=Max('transaction_at'))
    transactions = all_transactions
    if type_filter in ('deposit', 'withdrawal'):
        transactions = transactions.filter(type=type_filter)
    if date_from:
        transactions = transactions.filter(transaction_at__date__gte=date_from)
    if date_to:
        transactions = transactions.filter(transaction_at__date__lte=date_to)
    if search:
        field_map = {
            'description': 'description__icontains',
            'memo': 'memo__icontains',
            'transaction_type': 'transaction_type__icontains',
        }
        lookup = field_map.get(search_field, 'description__icontains')
        transactions = transactions.filter(**{lookup: search})

    total_deposit = transactions.filter(type='deposit').aggregate(total=Sum('amount'))['total'] or 0
    total_withdrawal = transactions.filter(type='withdrawal').aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'transactions/detail.html', {
        'ledger': ledger,
        'period_start': period['start'],
        'period_end': period['end'],
        'transactions': transactions,
        'total_deposit': total_deposit,
        'total_withdrawal': total_withdrawal,
        'last_balance': transactions.last().balance if transactions.exists() else 0,
        'net': total_deposit - total_withdrawal,
        'is_filtered': bool(type_filter or search or date_from or date_to),
        'type_filter': type_filter,
        'search_field': search_field,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
    })


RECEIPT_ALLOWED_EXTS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf')
RECEIPT_MAX_SIZE = 10 * 1024 * 1024


def _receipt_redirect(request, error=None):
    next_url = request.POST.get('next', '')
    if not next_url.startswith('/'):
        next_url = '/receipts/'
    if error:
        sep = '&' if '?' in next_url else '?'
        next_url = f'{next_url}{sep}error={error}'
    return redirect(next_url)


@login_required(login_url='login')
def receipt_status(request):
    year = request.GET.get('year', '')
    status = request.GET.get('status', 'missing')
    search = request.GET.get('search', '').strip()
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    base = Transaction.objects.filter(is_deleted=False, type='withdrawal')
    if year:
        base = base.filter(ledger__year=year)
    if date_from:
        base = base.filter(transaction_at__date__gte=date_from)
    if date_to:
        base = base.filter(transaction_at__date__lte=date_to)
    if search:
        base = base.filter(Q(description__icontains=search) | Q(memo__icontains=search))

    total_count = base.count()
    linked_count = base.filter(receipts__is_deleted=False).distinct().count()
    missing_count = total_count - linked_count

    transactions = base
    if status == 'missing':
        transactions = transactions.exclude(receipts__is_deleted=False)
    elif status == 'linked':
        transactions = transactions.filter(receipts__is_deleted=False).distinct()

    transactions = (
        transactions
        .select_related('ledger')
        .prefetch_related(Prefetch(
            'receipts',
            queryset=Receipt.objects.filter(is_deleted=False).select_related('upload'),
            to_attr='active_receipts',
        ))
        .order_by('transaction_at')
    )

    return render(request, 'receipts/status.html', {
        'transactions': transactions,
        'total_count': total_count,
        'linked_count': linked_count,
        'missing_count': missing_count,
        'years': TransactionLedger.objects.values_list('year', flat=True).order_by('-year'),
        'available_receipts': Receipt.objects.filter(is_deleted=False).order_by('-created_at'),
        'year': year,
        'status': status,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
        'error': request.GET.get('error', ''),
    })


@login_required(login_url='login')
def receipt_upload(request):
    if request.method != 'POST':
        return redirect('receipt_status')

    tx_ids = request.POST.getlist('transaction_ids')
    transactions = list(Transaction.objects.filter(
        pk__in=tx_ids, is_deleted=False, type='withdrawal'
    ))
    if not transactions:
        return _receipt_redirect(request, '연결할 출금 거래를 선택해주세요.')

    receipt_id = request.POST.get('receipt_id', '')
    if receipt_id:
        receipt = Receipt.objects.filter(pk=receipt_id, is_deleted=False).first()
        if receipt is None:
            return _receipt_redirect(request, '선택한 자료를 찾을 수 없습니다.')
    else:
        f = request.FILES.get('file')
        if f is None:
            return _receipt_redirect(request, '업로드할 파일을 선택해주세요.')
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in RECEIPT_ALLOWED_EXTS:
            return _receipt_redirect(request, '이미지 또는 PDF 파일만 업로드할 수 있습니다.')
        if f.size > RECEIPT_MAX_SIZE:
            return _receipt_redirect(request, '파일 크기는 10MB를 넘을 수 없습니다.')
        save_dir = os.path.join(settings.MEDIA_ROOT, 'receipts')
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, f'{uuid.uuid4().hex[:8]}_{f.name}')
        with open(file_path, 'wb') as out:
            for chunk in f.chunks():
                out.write(chunk)
        uploaded = UploadedFile.objects.create(
            file_name=f.name,
            file_path=file_path,
            file_type='receipt',
            uploaded_by=request.user,
        )
        receipt = Receipt.objects.create(
            upload=uploaded,
            name=request.POST.get('name', '').strip() or f.name,
        )

    receipt.transactions.add(*transactions)
    return _receipt_redirect(request)


@login_required(login_url='login')
def receipt_unlink(request, pk):
    receipt = get_object_or_404(Receipt, pk=pk, is_deleted=False)
    if request.method == 'POST':
        tx_id = request.POST.get('transaction_id')
        if tx_id:
            receipt.transactions.remove(tx_id)
    return _receipt_redirect(request)


@login_required(login_url='login')
def receipt_delete(request, pk):
    receipt = get_object_or_404(Receipt, pk=pk, is_deleted=False)
    if request.method == 'POST':
        receipt.is_deleted = True
        receipt.save()
    return _receipt_redirect(request)


@login_required(login_url='login')
def receipt_library(request):
    receipts = (
        Receipt.objects
        .filter(is_deleted=False)
        .select_related('upload', 'upload__uploaded_by')
        .prefetch_related(Prefetch(
            'transactions',
            queryset=Transaction.objects.filter(is_deleted=False).select_related('ledger').order_by('transaction_at'),
            to_attr='active_transactions',
        ))
        .order_by('-created_at')
    )
    return render(request, 'receipts/library.html', {
        'receipts': receipts,
        'error': request.GET.get('error', ''),
    })
