from django import forms
from .models import Role


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '권한명 입력'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '설명 입력 (선택)'}),
        }
        labels = {
            'name': '권한명',
            'description': '설명',
        }
