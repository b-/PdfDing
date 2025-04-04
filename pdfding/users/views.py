from random import randint
from uuid import uuid4

from allauth.account.utils import send_email_confirmation
from allauth.account.views import LoginView, PasswordResetDoneView, PasswordResetView, SignupView
from allauth.socialaccount.providers.openid_connect.views import callback, login
from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django_htmx.http import HttpResponseClientRefresh
from users import forms
from users.models import Profile
from users.service import create_demo_user, get_secondary_color


def account_settings(request):
    """View for the account settings page"""

    uses_social = request.user.socialaccount_set.exists()

    # pragma: no cover
    return render(request, 'account_settings.html', {'uses_social': uses_social})


def ui_settings(request):  # pragma: no cover
    """View for the ui settings page"""

    # pragma: no cover
    return render(request, 'ui_settings.html')


def danger_settings(request):  # pragma: no cover
    """View for the danger settings page"""

    # pragma: no cover
    return render(request, 'danger_settings.html')


class ChangeSetting(View):
    """View for changing the settings."""

    form_dict = {
        'email': forms.EmailForm,
        'theme': forms.create_user_field_form(['dark_mode']),
        'theme_color': forms.create_user_field_form(['theme_color']),
        'pdf_inverted_mode': forms.create_user_field_form(['pdf_inverted_mode']),
        'custom_theme_color': forms.CustomThemeColorForm,
        'show_progress_bars': forms.create_user_field_form(['show_progress_bars']),
    }

    def get(self, request: HttpRequest, field_name: str):
        """For a htmx request this will load a change pdfs per page form as a partial"""

        initial_dict = {
            'email': {'email': request.user.email},
            'theme': {'dark_mode': request.user.profile.dark_mode},
            'theme_color': {'theme_color': request.user.profile.theme_color},
            'custom_theme_color': {'custom_theme_color': request.user.profile.custom_theme_color},
            'pdf_inverted_mode': {'pdf_inverted_mode': request.user.profile.pdf_inverted_mode},
            'show_progress_bars': {'show_progress_bars': request.user.profile.show_progress_bars},
        }

        if request.htmx:
            form = self.form_dict[field_name](initial=initial_dict[field_name])

            return render(
                request,
                'partials/settings_form.html',
                {
                    'form': form,
                    'action_url': reverse('profile-setting-change', kwargs={'field_name': field_name}),
                    'edit_id': f'{field_name}_edit',
                },
            )

        return redirect('home')

    def post(self, request: HttpRequest, field_name: str):
        """Process the submitted change settings form"""

        if field_name == 'email':
            form = self.form_dict[field_name](request.POST, instance=request.user)
        else:
            form = self.form_dict[field_name](request.POST, instance=request.user.profile)

        if form.is_valid():
            if field_name == 'email':
                email = form.cleaned_data['email']
                if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                    messages.warning(request, f'{email} is already in use.')
                    return redirect('account_settings')
                form.save()

                # Then send confirmation email
                send_email_confirmation(request, request.user)
            elif field_name == 'custom_theme_color':
                form.save()

                # calculate shades for custom theme colors
                profile = request.user.profile
                profile.custom_theme_color_secondary = get_secondary_color(request.user.profile.custom_theme_color)
                profile.save()
            else:
                form.save()

        else:
            try:
                messages.warning(request, dict(form.errors)[field_name][0])
            except:  # noqa # pragma: no cover
                messages.warning(request, 'Input is not valid!')

        return redirect(request.META.get('HTTP_REFERER', 'account_settings'))


class ChangeSorting(View):
    """View for changing the sorting settings for the overviews"""

    def post(self, request: HttpRequest, sorting_category: str, sorting: str):
        """Change the sorting setting."""

        if request.htmx:
            user_profile = request.user.profile

            match sorting_category:
                case 'annotation_sorting':
                    user_profile.annotation_sorting = Profile.AnnotationsSortingChoice[str.upper(sorting)]
                case 'pdf_sorting':
                    user_profile.pdf_sorting = Profile.PdfSortingChoice[str.upper(sorting)]
                case 'shared_pdf_sorting':
                    user_profile.shared_pdf_sorting = Profile.SharedPdfSortingChoice[str.upper(sorting)]
                case 'user_sorting':
                    user_profile.user_sorting = Profile.UserSortingChoice[str.upper(sorting)]

            user_profile.save()

            return HttpResponseClientRefresh()

        return redirect('account_settings')


class ChangeLayout(View):
    """View for changing the layout settings for the pdf overview"""

    def post(self, request: HttpRequest, layout: str):
        """Change the layout setting."""

        if request.htmx:
            user_profile = request.user.profile
            user_profile.layout = Profile.LayoutChoice[str.upper(layout)]
            user_profile.save()

            return HttpResponseClientRefresh()

        return redirect('account_settings')


class ChangeTreeMode(View):
    """View for turning tag tree mode on and off."""

    def post(self, request: HttpRequest):
        """Change the sorting setting."""

        if request.htmx:
            user_profile = request.user.profile
            user_profile.tag_tree_mode = not user_profile.tag_tree_mode

            user_profile.save()

            return HttpResponseClientRefresh()

        return redirect('account_settings')


class OpenCollapseTags(View):
    """View for opening and collapsing tags in the pdf overview"""

    def post(self, request: HttpRequest):
        """Open or collapse the tags in the pdf overview"""

        if request.htmx:
            user_profile = request.user.profile
            user_profile.tags_open = not user_profile.tags_open

            user_profile.save()

            return HttpResponseClientRefresh()

        return redirect('account_settings')


class Delete(View):
    """View for deleting a user profile."""

    def get(self, request: HttpRequest):  # pragma: no cover
        """Display the page for deleting the user"""

        return render(request, 'profile_delete.html')

    def post(self, request: HttpRequest):
        """Delete the user"""

        user = request.user

        logout(request)
        user.delete()
        messages.success(request, 'Your Account was successfully deleted.')

        return redirect('home')


@method_decorator(login_not_required, name="dispatch")
class CreateDemoUser(View):
    """View for creating demo users"""

    def post(self, request: HttpRequest):
        """Create a demo user."""

        if request.htmx and django_settings.DEMO_MODE:
            password = 'demo'  # nosec
            max_user_number = django_settings.DEMO_MAX_USERS

            if User.objects.all().count() < max_user_number:
                email = f'{str(uuid4())[:8]}@pdfding.com'

                try:
                    user = create_demo_user(email, password)
                # if for some reason the email is already used, return the user instead of creating it.
                except IntegrityError:
                    user = User.objects.get(email=email)
            # don't create new users if there are too many already
            else:
                user = User.objects.get(id=randint(1, max_user_number))  # nosec

            return render(request, 'partials/demo_user.html', {'email': user.email, 'password': password})

        return redirect('pdf_overview')


@method_decorator(login_not_required, name="dispatch")
class PdfDingLoginView(LoginView):
    """
    Overwrite allauths login to be accessed without being logged in
    """

    @login_not_required
    def dispatch(self, request, *args, **kwargs):
        return super(PdfDingLoginView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_not_required, name="dispatch")
class PdfDingSignupView(SignupView):
    """
    Overwrite allauths signup to be accessed without being logged in
    """

    @login_not_required
    def dispatch(self, request, *args, **kwargs):
        return super(PdfDingSignupView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_not_required, name="dispatch")
class PdfDingPasswordResetView(PasswordResetView):
    """
    Overwrite allauths password reset to be accessed without being logged in
    """

    @login_not_required
    def dispatch(self, request, *args, **kwargs):
        return super(PdfDingPasswordResetView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_not_required, name="dispatch")
class PdfDingPasswordResetDoneView(PasswordResetDoneView):
    """
    Overwrite allauths password reset done to be accessed without being logged in
    """

    @login_not_required
    def dispatch(self, request, *args, **kwargs):
        return super(PdfDingPasswordResetDoneView, self).dispatch(request, *args, **kwargs)


@login_not_required
def pdfding_oidc_login(request: HttpRequest):  # pragma: no cover
    """
    Overwrite allauths oidc login to be accessed without being logged in
    """

    return login(request, 'oidc')


@login_not_required
def pdfding_oidc_callback(request: HttpRequest):  # pragma: no cover
    """
    Overwrite allauths oidc callback to be accessed without being logged in
    """

    return callback(request, 'oidc')
