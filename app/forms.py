from django import forms
from .models import Role


class RoleForm(forms.ModelForm):
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
