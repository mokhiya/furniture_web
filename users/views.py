from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from users.form import RegistrationForm, LoginForm
from users.token import email_verification_token



def verify_email(request, uidb64, token):
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=uid)
    if user is not None and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account activated')
        return redirect(reverse_lazy('users:login'))
    else:
        messages.error(request, 'The verification link is invalid.')
        return redirect(reverse_lazy('users:login'))


def send_email_verification(request, user):
    token = email_verification_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    current_site = get_current_site(request)
    verification_url = reverse('users:verify_email', kwargs={'uidb64': uid, 'token': token})
    full_url = f"http://{current_site.domain}/{verification_url}"

    text_content = render_to_string(
        'registration/verify-email.html',
        {
            'user': user,
            'full_url': full_url,
        }
    )

    message = EmailMultiAlternatives(
        subject='Email Verification',
        body=text_content,
        to=[user.email],
        from_email=settings.EMAIL_HOST_USER
    )
    message.attach_alternative(text_content, 'text/html')
    message.send()


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False
            user.save()
            send_email_verification(request, user)
            return redirect(reverse_lazy('users:login'))
        else:
            errors = form.errors
            return render(request, 'registration/user-register.html', {"errors": errors})
    return render(request, 'registration/user-register.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request=request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                messages.error(request, 'Invalid username or password')
                return render(request, template_name='registration/user-login.html')
    else:
        return render(request, 'registration/user-login.html')


def logout_view(request):
    return HttpResponse("logout")
