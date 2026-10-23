# django.contrib.messages is used to display one-time notifications to the user, such as success or error messages. It provides a way to store messages in the session and retrieve them for display in the next request.

from django.contrib import messages

# django.contrib.auth.authenticate is used to verify a user's credentials (username and password) and return a User object if the credentials are valid. It checks the provided username and password against the database and returns the corresponding User object if authentication is successful, or None if authentication fails.

# django.contrib.auth.login is used to log a user in by creating a session for the authenticated user. It takes the request object and the authenticated User object as parameters and establishes a session for the user, allowing them to access protected views and resources.

# django.contrib.auth.logout is used to log a user out by terminating their session. It takes the request object as a parameter and removes the user's session data, effectively logging them out of the application.

from django.contrib.auth import authenticate,get_user_model,login, logout

# django.contrib.auth.decorators.login_required is a decorator that can be applied to views to restrict access to authenticated users only. It checks if the user is logged in before allowing access to the view. If the user is not authenticated, they will be redirected to the login page.

from django.contrib.auth.decorators import login_required

# django.shortcuts.redirect is used to redirect the user to a different URL or view. It takes the target URL or view name as a parameter and returns an HTTP response that instructs the browser to navigate to the specified location.

# django.shortcuts.render is used to render a template and return an HTTP response. It takes the request object, the template name, and an optional context dictionary as parameters. The context dictionary contains data that can be accessed within the template for dynamic rendering.


from django.shortcuts import redirect, render

# django.views.decorators.http.require_POST is a decorator that can be applied to views to restrict access to only POST requests. It ensures that the view can only be accessed via a POST request, and if a different HTTP method is used, it will return a 405 Method Not Allowed response.

from django.views.decorators.http import require_POST

# .forms is a module that contains the form classes used in the accounts app. It is imported to access the CustomerRegistrationForm class, which is used for user registration.
from .forms import CustomerRegistrationForm

from cart.cart import merge_session_cart

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from django.utils.encoding import force_bytes, force_str

from django.utils.http import (
urlsafe_base64_decode,
urlsafe_base64_encode,
)
from django.urls import reverse

def register(request):

    if request.user.is_authenticated:
        return redirect("accounts:profile")
    
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            # Create the user but do not allow login before activation.
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            # Generate a unique user ID and activation token.
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)   

            # Build the complete activation URL.
            activation_path = reverse(
                        "accounts:activate",
                        kwargs={"uidb64": uid, "token": token},
                    )
            
            activation_url = request.build_absolute_uri(activation_path)
            
            subject = "Activate your Uttarakhand Store account"

            message = (
            f"Hello {user.username},\n\n"
            "Thank you for registering with Uttarakhand Store.\n\n"
            "Please click the link below to activate your account:\n\n"
            f"{activation_url}\n\n"
            "If you did not create this account, you can ignore this email."
           )
            try:
                send_mail(
                subject=subject,
                message=message,
                from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings.
                recipient_list=[user.email],
                fail_silently=False,
            )
            except Exception:
                 # The user is saved but remains inactive if email sending fails.
                messages.error(
                    request,
                    "Your account was created, but the activation email "
                    "could not be sent. Please try again later or contact support.",
                )
                return redirect("accounts:activation_sent")     
            
            messages.success(
            request,
            "Registration successful! Check your email to activate your account.",
            )
            return redirect("accounts:activation_sent")
    else:
        form = CustomerRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})

def activation_sent(request):
    return render(
        request,
        "accounts/activation_sent.html",
    )

def activate(request, uidb64, token):
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None

    if(user is not None and default_token_generator.check_token(user, token)):
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])

            messages.success(
                request,
                "Your email has been verified! You can now log in."
            )
            return redirect("accounts:login")

    messages.error(
        request,
        "This activation link is invalid or has expired."
    )
    return redirect("accounts:register")
    
def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    if request.method == "POST":
        username = request.POST.get("username","").strip()
        password = request.POST.get("password","")

        # authenticate is used to verify the user's credentials (username and password) against the database. It checks if the provided username and password match an existing user account. If the credentials are valid, it returns a User object; otherwise, it returns None.
        # authenticate(request, username=username, password=password) here request is passed to the authenticate function to provide context for the authentication process. It allows the authentication backend to access information about the current request, such as session data or user agent, which may be relevant for authentication decisions. By passing the request object, the authentication process can take into account any additional factors that may affect the authentication outcome. If request is not passed, the authentication process may not have access to certain contextual information that could be important for determining the validity of the credentials. This could potentially lead to incorrect authentication results or security vulnerabilities. if pass like authenticate(username=username, password=password) without request, the authentication backend may not have access to the necessary context to make accurate authentication decisions. This could result in false positives or false negatives during the authentication process, potentially allowing unauthorized access or denying access to legitimate  users. Like check CSRF tokens, session data, or user agent information. These factors can be important for determining the authenticity of the request and the validity of the provided credentials. By passing the request object, the authentication backend can consider these additional factors and make more informed decisions about whether to authenticate the user or not.
        

        # login is used to log the user in by creating a session for the authenticated user.
        # login(request, user) here request is passed to the login function to establish a session for the authenticated user. It allows the login process to associate the user's session with the current request, enabling the application to maintain the user's authenticated state across multiple requests. By passing the request object, the login function can access and modify the session data associated with the current request, ensuring that the user's authentication status is properly maintained throughout their interaction with the application. If request is not passed, the login process may not have access to the necessary context to establish a session for the user. This could result in the user being logged in but not having their session properly associated with their requests, leading to issues such as losing authentication state or being treated as an unauthenticated user on subsequent requests. By passing the request object, the login function can ensure that the user's session is correctly established and maintained, allowing for a seamless and secure user experience.
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Restore saved cart and merge guest cart.
            merge_session_cart(request)
            messages.success(request, "You have successfully logged in.")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Invalid username or password.")
    # how to access the login.html template in the accounts app from the views.py file? The login.html template can be accessed by specifying the path to the template in the render function. In this case, the template is located in the "accounts" app, so the path is specified as "accounts/login.html". This tells Django to look for the login.html template within the templates directory of the accounts app. By providing this path, Django can locate and render the appropriate template when rendering the login view.
    return render(request, "accounts/login.html")

@require_POST
def logout_view(request):
    # logout is used to log the user out by terminating their session.
    # logout(request) here request is passed to the logout function to terminate the user's session. It allows the logout process to access and modify the session data associated with the current request, effectively logging the user out of the application. By passing the request object, the logout function can clear the session data and remove any authentication-related information, ensuring that the user is properly logged out and their session is terminated. If request is not passed, the logout process may not have access to the necessary context to terminate the user's session. This could result in the user remaining logged in or their session not being properly cleared, leading to potential security risks or unexpected behavior. By passing the request object, the logout function can ensure that the user's session is correctly terminated, providing a secure and reliable logout experience.
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("accounts:login")

@login_required
def profile(request):
    return render(request, "accounts/profile.html")
