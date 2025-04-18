from admin.service import get_latest_version
from base import base_views
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.db.models.functions import Lower
from django.http import Http404, HttpRequest
from django.shortcuts import redirect, render
from django.views import View
from django_htmx.http import HttpResponseClientRefresh
from pdf.models import Pdf


class BaseAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_superuser and self.request.user.is_staff:
            return True
        else:
            raise Http404("Given query not found...")


class BaseAdminMixin:
    obj_name = 'user'


class OverviewMixin(BaseAdminMixin):
    overview_page_name = 'user_overview_page'

    @staticmethod
    def get_sorting(request: HttpRequest):
        """Get the sorting of the overview page."""

        profile = request.user.profile

        sorting_dict = {
            'Newest': '-date_joined',
            'Oldest': 'date_joined',
            'Email_asc': Lower('email'),
            'Email_desc': Lower('email').desc(),
        }

        return sorting_dict[profile.user_sorting]

    @staticmethod
    def filter_objects(request: HttpRequest) -> QuerySet:
        """
        Filter the PDFs when performing a search in the overview.
        """

        users = User.objects.all()

        search = request.GET.get('search', '')
        tags = request.GET.get('tags', [])
        if tags:
            tags = tags.split(' ')

        if 'admin' in tags:
            users = users.filter(is_superuser=True)

        if search:
            users = users.filter(email__icontains=search)

        return users

    @staticmethod
    def get_extra_context(request: HttpRequest) -> dict:
        """get further information that needs to be passed to the template."""

        tag_query = request.GET.get('tags', [])
        if tag_query:
            tag_query = tag_query.split(' ')

        extra_context = {
            'search_query': request.GET.get('search', ''),
            'tag_query': tag_query,
            'page': 'user_overview',
        }

        return extra_context


class AdminMixin(BaseAdminMixin):
    @staticmethod
    def get_object(_, identifier: str):
        user = User.objects.get(id=identifier)

        return user


class Overview(BaseAdminRequiredMixin, OverviewMixin, base_views.BaseOverview):
    """
    View for the user overview page. This view performs the searching and sorting of the users. It's also responsible
    for paginating the users.
    """


class OverviewQuery(base_views.BaseOverviewQuery):
    """View for performing searches and sorting on the user overview page."""

    obj_name = 'user'


class DeleteProfile(BaseAdminRequiredMixin, AdminMixin, base_views.BaseDelete):
    """View for deleting a user profile"""


class AdjustAdminRights(BaseAdminRequiredMixin, View):
    """View for adjusting the admin rights"""

    def post(self, request: HttpRequest, identifier: str):
        """Delete the user"""

        if request.htmx:
            user = User.objects.get(id=identifier)

            if user.is_staff and user.is_superuser:
                user.is_staff = False
                user.is_superuser = False
            else:
                user.is_staff = True
                user.is_superuser = True

            user.save()

            return HttpResponseClientRefresh()

        return redirect('user_overview')


class Information(View):  # pragma: no cover
    """View for getting instance information"""

    def get(self, request: HttpRequest):
        """Get instance information"""

        number_of_users = User.objects.all().count()
        number_of_pdfs = Pdf.objects.all().count()
        latest_version = get_latest_version()

        context = {
            'number_of_users': number_of_users,
            'number_of_pdfs': number_of_pdfs,
            'current_version': settings.VERSION,
            'latest_version': latest_version,
        }

        return render(request, 'information.html', context=context)
