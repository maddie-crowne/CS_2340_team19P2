from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    """
    A custom user creation form that extends the default UserCreationForm.

    This form includes additional fields for first name, last name, and email address.
    It ensures that all fields are validated before creating a new user instance.

    Attributes:
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        email (str): The email address of the user.
    """
    first_name = forms.CharField(max_length=30, required=True, help_text='Required')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        """
        Meta class for CustomUserCreationForm.

        This inner class defines the model associated with this form and the
        fields that will be included in the form.

        Attributes:
            model (Model): The User model being created.
            fields (tuple): A tuple specifying the fields that will be included in the form,
                            including username, first_name, last_name, email, and password.
        """
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        """
        Saves the user instance, including additional fields.

        This method overrides the default save method to include the first name,
        last name, and email address in the user instance. If `commit` is True,
        the user instance is saved to the database.

        :param commit: If True, the user instance is saved to the database.
                        If False, the user instance is returned without saving.
        :return: The user instance that has been updated (and possibly saved).
        """
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user
