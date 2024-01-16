from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreationForm(forms.ModelForm):
    new_password = forms.CharField(
        label="New Password", widget=forms.PasswordInput, required=False, min_length=6
    )

    class Meta:
        model = User
        fields = "__all__"

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        password = self.cleaned_data.get("new_password", "")
        if len(password) > 0:
            user.set_password(password)
        user.save()
        return user
