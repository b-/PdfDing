from django.urls import path
from users import views

urlpatterns = [
    path('account_settings', views.account_settings, name="account_settings"),
    path('danger_settings', views.danger_settings, name="danger_settings"),
    path('ui_settings', views.ui_settings, name="ui_settings"),
    path('viewer_settings', views.viewer_settings, name="viewer_settings"),
    path('delete', views.Delete.as_view(), name="profile-delete"),
    path('change_setting/<field_name>', views.ChangeSetting.as_view(), name="profile-setting-change"),
    path('create_demo_user', views.CreateDemoUser.as_view(), name="create_demo_user"),
    path('change_layout/<layout>', views.ChangeLayout.as_view(), name="change_layout"),
    path('change_sorting/<sorting_category>/<sorting>', views.ChangeSorting.as_view(), name="change_sorting"),
    path('change_tree_mode', views.ChangeTreeMode.as_view(), name="change_tree_mode"),
    path('open_collapse_tags', views.OpenCollapseTags.as_view(), name="open_collapse_tags"),
]
