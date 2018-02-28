import codecs
import csv

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.sites.shortcuts import get_current_site
from django.http.response import HttpResponse, HttpResponseBadRequest, Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from ocd import settings
from ocd.base_views import CommunityMixin
from users import models
from .default_roles import DefaultGroups
from users.forms import InvitationForm, QuickSignupForm, ImportInvitationsForm, OCPasswordResetConfirmForm
from users.models import Invitation, OCUser, Membership, UnsubscribeUser


def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'

    class K:
        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0

    return K


def _cmp_func(a, b):
    res = ((a['board'] > b['board']) - (a['board'] < b['board'])) * -1
    if res == 0:
        return (a['board'] > b['board']) - (a['board'] < b['board'])
    else:
        return res


cmp_func = cmp_to_key(_cmp_func)


class MembershipMixin(CommunityMixin):
    model = models.Membership

    def get_queryset(self):
        return models.Membership.objects.filter(community=self.community)

    def validate_invitation(self, email):
        # somewhat of a privacy problem next line. should probably fail silently
        if Membership.objects.filter(community=self.community,
                                     user__email=email).exists():
            return HttpResponseBadRequest(
                _("This user already a member of this community."))

        if Invitation.objects.filter(community=self.community,
                                     email=email).exists():
            return HttpResponseBadRequest(
                _("This user is already invited to this community."))
        return None


class MembershipList(MembershipMixin, ListView):
    required_permission = 'community.invite_member'

    def get_context_data(self, **kwargs):
        d = super(MembershipList, self).get_context_data(**kwargs)

        d['invites'] = Invitation.objects.filter(community=self.community)
        d['form'] = InvitationForm(initial={'message': Invitation.DEFAULT_MESSAGE % _('The board')})
        d['members_list'] = Membership.objects.filter(community=self.community)
        # d['board_list'] = Membership.objects.board().filter(community=self.community)
        # d['member_list'] = Membership.objects.none_board().filter(community=self.community)
        # d['board_name'] = self.community.board_name

        return d

    def post(self, request, *args, **kwargs):

        form = InvitationForm(request.POST)

        if not form.is_valid():
            return HttpResponseBadRequest(
                _("Form error. Please supply a valid email."))

        v_err = self.validate_invitation(form.instance.email)
        if v_err:
            return v_err

        form.instance.default_group_name = DefaultGroups.BOARD
        form.instance.community = self.community
        form.instance.created_by = request.user

        i = form.save()
        i.send(sender=request.user, recipient_name=form.cleaned_data['name'])

        return render(request, 'users/_invitation.html', {'object': i})


class DeleteInvitationView(CommunityMixin, DeleteView):
    required_permission = 'community.invite_member'

    model = models.Invitation

    def get_queryset(self):
        return self.model.objects.filter(community=self.community)

    def get(self, request, *args, **kwargs):
        return HttpResponse("?")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponse("OK")


class UnsubscribeView(View):
    def get(self, request, *args, **kwargs):
        try:
            user = OCUser.objects.get(uid=self.kwargs.get('uid', 'xxx'))
        except OCUser.DoesNotExist:
            raise Http404
        user.opt_in = False
        user.save()

        UnsubscribeUser.objects.create(user=user)

        return HttpResponse(
            _('Email address [{}] has been successfully removed from out list'.format(user.email.lower())))


class AcceptInvitationView(DetailView):
    slug_field = 'code'
    slug_url_kwarg = 'code'
    model = models.Invitation

    form = None

    def get_form(self):
        if self.request.method == "POST":
            return QuickSignupForm(self.request.POST)
        else:
            return QuickSignupForm(initial={'display_name': self.get_object().name})

    def get_context_data(self, **kwargs):
        d = super(AcceptInvitationView, self).get_context_data(**kwargs)
        d['user_exists'] = OCUser.objects.filter(email=self.get_object().email
                                                 ).exists()
        d['path'] = self.request.path
        d['login_path'] = reverse('login') + "?next=" + self.request.path
        d['form'] = self.form if self.form else self.get_form()
        return d

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            return render(request, 'users/invitation404.html', {'base_url': settings.HOST_URL})
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):

        i = self.get_object()

        def create_membership(user):
            try:
                m = Membership.objects.get(user=user, community=i.community)
            except Membership.DoesNotExist:
                m = Membership.objects.create(user=user, community=i.community,
                                              default_group_name=i.default_group_name,
                                              invited_by=i.created_by)
            i.delete()
            return m

        if request.user.is_authenticated:
            if 'join' in request.POST:
                m = create_membership(request.user)
                return redirect(m.community.get_absolute_url())

        else:
            if 'signup' in request.POST:
                self.form = self.get_form()
                if self.form.is_valid():
                    # Quickly create a user :-)
                    self.form.instance.email = i.email
                    u = self.form.save()
                    m = create_membership(u)
                    # TODO Send email with details
                    user = authenticate(email=self.form.instance.email,
                                        password=self.form.cleaned_data['password1'])
                    login(request, user)
                    return redirect(m.community.get_absolute_url())

        messages.warning(request,
                         _("Oops. Something went wrong. Please try again."))
        return self.get(request, *args, **kwargs)


class AutocompleteMemberName(MembershipMixin, ListView):
    required_permission = 'issues.editopen_issue'

    def get_queryset(self):
        members = super(AutocompleteMemberName, self).get_queryset()
        limit = self.request.GET.get('limit', '')
        if limit == 'm':
            members = members.filter(default_group_name='member')
        q = self.request.GET.get('q', '')
        if q:
            members = members.filter(
                user__is_active=True,
                user__display_name__istartswith=q)
        else:
            members = members.filter(user__is_active=True)
            if members.count() > 75:
                return None

        return members

    def get(self, request, *args, **kwargs):

        members = self.get_queryset()
        if not members:
            return JsonResponse({})
        else:
            members = list(members.values('user__display_name', 'user__id', 'default_group_name'))
            for m in members:
                m['tokens'] = [m['user__display_name'], ]
                m['value'] = m['user__display_name']
                m['board'] = m['default_group_name'] != 'member'
            members.sort(key=cmp_func)
            context = self.get_context_data(object_list=members)
            return JsonResponse(members, safe=False)


class MemberProfile(MembershipMixin, DetailView):
    required_permission = 'users.show_member_profile'

    model = models.Membership
    template_name = "users/member_profile.html"

    def get_context_data(self, **kwargs):
        d = super(MemberProfile, self).get_context_data(**kwargs)
        d['form'] = ""
        d['belongs_to_board'] = self.get_object().default_group_name != DefaultGroups.MEMBER
        d['member_late_tasks'] = self.object.member_late_tasks(user=self.request.user, community=self.community)
        d['member_open_tasks'] = self.object.member_open_tasks(user=self.request.user, community=self.community)
        d['member_close_tasks'] = self.object.member_close_tasks(user=self.request.user, community=self.community)
        return d


class ImportInvitationsView(MembershipMixin, FormView):
    form_class = ImportInvitationsForm
    template_name = 'users/import_invitations.html'

    def form_valid(self, form):
        uploaded_file = self.request.FILES['csv_file']
        uploaded_csvfile = csv.DictReader(codecs.iterdecode(uploaded_file, 'utf-8'),
                                          fieldnames=['name', 'email', 'role'])
        roles = dict(DefaultGroups.CHOICES)
        sent = 0
        for row in uploaded_csvfile:
            role = list(roles.keys())[0]
            name = row['name']
            firstname = row['firstname']
            lastname = row['lastname']
            email = row['email']
            if not email:
                continue
            _role = row['role']
            try:
                for k, v in roles.items():
                    if v == _role:
                        role = k
            except:
                role = list(roles.keys())[0]

            if OCUser.objects.filter(email=email.lower()).exists():
                continue

            if name:
                fullname = name
            else:
                fullname = u'{}{}'.format(firstname, u' {}'.format(lastname) if lastname else '')
            user = OCUser.objects.create_user(
                email=email.lower(),
                display_name=fullname,
                password='opcomm'
            )
            membership = Membership.objects.create(
                community=self.community,
                user=user,
                default_group_name=role,
                invited_by=self.request.user
            )
            sent += 1

        messages.success(self.request, _('%d Invitations sent') % (sent,))
        return redirect(reverse('members', kwargs={'community_id': self.community.id}))

    @method_decorator(permission_required('is_superuser'))
    def dispatch(self, *args, **kwargs):
        return super(ImportInvitationsView, self).dispatch(*args, **kwargs)


@csrf_protect
def oc_password_reset(request, is_admin_site=False,
                      template_name='registration/password_reset_form.html',
                      email_template_name='registration/password_reset_email.html',
                      subject_template_name='registration/password_reset_subject.txt',
                      password_reset_form=PasswordResetForm,
                      token_generator=default_token_generator,
                      post_reset_redirect=None,
                      from_email=None,
                      current_app=None,
                      extra_context=None):
    if post_reset_redirect is None:
        post_reset_redirect = reverse('django.contrib.auth.views.password_reset_done')
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            current_site = get_current_site(request)
            from_email = "%s <%s>" % (current_site.name, settings.FROM_EMAIL)
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
        email = request.POST['email']
        try:
            invitation = Invitation.objects.get(email=email)
            extra_context = {
                'has_invitation': True,
            }
            invitation.send(sender=invitation.created_by,
                            recipient_name=invitation.name)
            # TODO: redirect to message
        #             return HttpResponseRedirect(reverse('invitation_sent'))
        except Invitation.DoesNotExist:
            pass
    else:
        form = password_reset_form()
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)


class OCPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = OCPasswordResetConfirmForm
