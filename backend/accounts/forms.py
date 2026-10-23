
# django.forms is a module that provides classes and functions for creating and handling forms in Django. It allows you to define form fields, validation rules, and rendering options for user input.

from django import forms

# django.contrib.auth.forms.UserCreationForm is a built-in form class that provides a user registration form with fields for username, password, and password confirmation. It includes built-in validation for password strength and matching passwords.

from django.contrib.auth.forms import UserCreationForm

# django.contrib.auth.models.User is the default User model provided by Django's authentication system. It represents a user account and includes fields such as username, email, password, and other user-related information. It is used for authentication and authorization purposes in Django applications.

from django.contrib.auth.models import User


class CustomerRegistrationForm(UserCreationForm):
    # forms.EmailField is used to create an email input field in the form. The required=True argument ensures that the email field must be filled out by the user when submitting the form.
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
     # The clean_email method is a custom validation method that checks if the email provided by the user already exists in the database. It retrieves the email from the cleaned_data dictionary, strips any leading or trailing whitespace, and converts it to lowercase. Then, it checks if a User object with the same email (case-insensitive) already exists in the database. If it does, a ValidationError is raised with an appropriate error message. If the email is unique, it is returned for further processing.
     # clean_email is overridden to customize the validation behavior of the email field. It checks if the email already exists in the User model and raises a ValidationError if it does. The cleaned_data dictionary is used to access the cleaned and validated data from the form fields.
    def clean_email(self):
        
        # self.cleaned_data is a dictionary that contains the cleaned and validated data from the form fields. It is populated after the form is submitted and validated. The cleaned_data dictionary allows you to access the values of the form fields after they have been processed and validated.

        email = self.cleaned_data["email"].strip().lower()
        # email__iexact is a case-insensitive lookup that checks if the email already exists in the User model. The filter method is used to retrieve all User objects that match the given email. If any matching User objects are found, it means that an account with the same email already exists, and a ValidationError is raised.
        #difference between __icontains and __iexact is that __icontains performs a case-insensitive search for a substring within a field, while __iexact performs a case-insensitive search for an exact match of the entire field value. In this case, we want to check if the email already exists in the database, so we use __iexact to ensure an exact match regardless of case.

        if User.objects.filter(email__iexact = email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email
    # The save method is overridden to customize the saving behavior of the form. It first calls the parent class's save method with commit=False to create a User object without saving it to the database yet. Then, it sets the email attribute of the User object to the cleaned email value from the form. If commit is True, it saves the User object to the database. Finally, it returns the User object.
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

        return user
