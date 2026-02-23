from django import forms
from accounts.models import User, Profile

class RegisterForm(forms.ModelForm):
    """
    Modelo form para registro de usuario
    """
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "username", "display_name"]

    def clean_password(self):
        """
        Validación de coincidencia de contraseñas
        """
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise forms.ValidationError("No coinciden las contraseñas")
        return cleaned

    def save(self, commit=True):
        """
        Funcion para hashear la contraseña
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """
    Modelo form para login de usuario
    """
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class ProfileForm(forms.ModelForm):
    """
    Modelo form para registrar perfiles de usuario
    """
    class Meta:
        model = Profile
        fields = ["empresa", "telefono", "preferencia"]
