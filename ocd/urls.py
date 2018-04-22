from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView, PasswordResetDoneView, PasswordResetCompleteView
from django.urls import path, include, reverse_lazy, re_path
from django.contrib import admin
from django.views.i18n import JavaScriptCatalog

import users
from meetings.views import MeetingCreateView
from . import views
from users.forms import OCPasswordResetForm
from users.models import CODE_LENGTH
from users.views import AcceptInvitationView, UnsubscribeView
from communities.views import MeetingAttachmentDeleteView, MeetingAttachmentDownloadView, About, CommunityList

urlpatterns = [
    # path('', communities.views.LandingPage.as_view(), name='landing'),
    # path('communities/', communities.views.CommunityList.as_view(), name='home'),
    path('', CommunityList.as_view(), name='home'),
    path('about/', About.as_view(), name='about'),
    path('<int:community_id>/remove-meeting-attachment/<int:pk>/', MeetingAttachmentDeleteView.as_view(),
         name="meeting_attachment_delete"),
    path('<int:community_id>/download-meeting-attachment/<int:pk>/',
         MeetingAttachmentDownloadView.as_view(),
         name="meeting_attachment_download"),
    path('<int:pk>/', include('communities.urls')),
    path('<int:community_id>/upcoming/close/', MeetingCreateView.as_view(), name="upcoming_close"),
    path('<int:community_id>/members/', include('users.urls')),
    path('<int:community_id>/issues/', include('issues.urls')),
    path('<int:community_id>/history/', include('meetings.urls')),
    path('login/', views.login_user, {'template_name': 'login.html'}, name="login"),
    path('logout/', LogoutView.as_view(), {'next_page': reverse_lazy('home')}, name="logout"),
    re_path('unsubscribe/(?P<uid>[a-z0-9]{32})/', UnsubscribeView.as_view(), name="unsubscribe"),
    re_path('invitation/(?P<code>[a-z0-9]{%d})/' % CODE_LENGTH, AcceptInvitationView.as_view(),
            name="accept_invitation"),
    path('user/password/reset/', users.views.oc_password_reset,
         {'post_reset_redirect': '/user/password/reset/done/', 'password_reset_form': OCPasswordResetForm},
         name="password_reset"),
    path('user/password/reset/done/', PasswordResetDoneView.as_view()),
    path('reset/<uidb64>/<token>/', users.views.OCPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('user/password/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('admin/', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),
    path('jsi18n/', JavaScriptCatalog.as_view(packages=['issues', 'communities']), name='javascript-catalog'),
    # E-Mail Pixel code
    re_path('p/(?P<pixel>\w+).gif/', users.views.EmailPixelView.as_view(), name='email_pixel'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
