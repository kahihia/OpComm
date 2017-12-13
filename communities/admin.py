from communities import models
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin, TabularInline
from users.models import Membership


class CommunityConfidentialReasonInline(TabularInline):
    model = models.CommunityConfidentialReason
    fk_name = 'community'
    extra = 0


class CommunityMembershipInline(TabularInline):
    model = Membership
    fk_name = 'community'
    extra = 1


class CommunityAdmin(ModelAdmin):

    fields = ('name', 'board_name', 'official_identifier', 'logo', 'is_public',
              'straw_voting_enabled', 'issue_ranking_enabled',
              'allow_links_in_emails', 'register_missing_board_members',
              'email_invitees', 'inform_system_manager', 'no_meetings_community')

    inlines = [CommunityConfidentialReasonInline, CommunityMembershipInline]


admin.site.register(models.Community, CommunityAdmin)
