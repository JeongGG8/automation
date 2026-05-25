from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator as _UserAttributeSimilarityValidator,
    MinimumLengthValidator as _MinimumLengthValidator,
    CommonPasswordValidator as _CommonPasswordValidator,
    NumericPasswordValidator as _NumericPasswordValidator,
)
from django.core.exceptions import ValidationError


class UserAttributeSimilarityValidator(_UserAttributeSimilarityValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError('비밀번호가 개인 정보와 너무 유사합니다.')

    def get_help_text(self):
        return '비밀번호는 개인 정보와 유사하지 않아야 합니다.'


class MinimumLengthValidator(_MinimumLengthValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(f'비밀번호가 너무 짧습니다. 최소 {self.min_length}자 이상이어야 합니다.')

    def get_help_text(self):
        return f'비밀번호는 최소 {self.min_length}자 이상이어야 합니다.'


class CommonPasswordValidator(_CommonPasswordValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError('너무 일반적으로 사용되는 비밀번호입니다.')

    def get_help_text(self):
        return '자주 사용되는 비밀번호는 사용할 수 없습니다.'


class NumericPasswordValidator(_NumericPasswordValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError('비밀번호가 숫자로만 이루어져 있습니다.')

    def get_help_text(self):
        return '비밀번호는 숫자로만 구성될 수 없습니다.'
