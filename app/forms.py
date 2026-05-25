from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Role, User


class RoleCreateForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['code', 'name', 'description', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '권한 코드 입력 (예: ADMIN)'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '권한명 입력'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '설명 입력 (선택)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'code': '권한 코드',
            'name': '권한명',
            'description': '설명',
            'is_active': '활성화',
        }


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'name', 'role', 'is_active', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '아이디 입력'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '실명 입력 (선택)'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'username': '아이디',
            'name': '실명',
            'role': '권한',
            'is_active': '활성화',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = '필수 항목입니다. 150자 이하, 영문·숫자·@/./+/-/_ 만 사용 가능합니다.'
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '비밀번호 입력'})
        self.fields['password1'].label = '비밀번호'
        self.fields['password1'].help_text = '8자 이상이어야 하며, 너무 단순한 비밀번호는 사용할 수 없습니다.'
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '비밀번호 확인'})
        self.fields['password2'].label = '비밀번호 확인'
        self.fields['password2'].help_text = '확인을 위해 동일한 비밀번호를 다시 입력하세요.'
        self.fields['role'].empty_label = '권한 없음'
        self.fields['is_active'].help_text = '활성화 해제 시 해당 계정으로 로그인할 수 없습니다. 계정 삭제 대신 이 옵션을 사용하세요.'


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'role', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '실명 입력 (선택)'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': '실명',
            'role': '권한',
            'is_active': '활성화',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].empty_label = '권한 없음'


class RoleEditForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '권한명 입력'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '설명 입력 (선택)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': '권한명',
            'description': '설명',
            'is_active': '활성화',
        }
