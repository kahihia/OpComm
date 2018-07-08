from django.contrib import admin
from django.contrib.admin import site
from django.utils.translation import ugettext_lazy as _
from issues import models
from meetings.models import AgendaItem


class IssueAgendaItemInline(admin.TabularInline):
    model = AgendaItem
    extra = 0


class IssueCommentInline(admin.StackedInline):
    model = models.IssueComment
    extra = 0
    readonly_fields = (
        'version',
        'uid',
    )
    exclude = (
        'ordinal',
    )


class ReferenceInline(admin.StackedInline):
    model = models.Reference
    extra = 0
    readonly_fields = (
        'version',
        'uid',
    )


class ProposalInline(admin.TabularInline):
    model = models.Proposal
    extra = 0


class RankingInline(admin.TabularInline):
    model = models.IssueRankingVote
    extra = 0


class IssueAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'community',
        'created_at',
        'status',
        'active',
        'order_by_votes',
        'proposal_count',
        'comment_count',
        'reference_count',
        'meeting_count',
    )
    list_filter = (
        'community',
        'status',
        'active',
    )
    search_fields = (
        'title',
    )
    date_hierarchy = 'created_at'
    inlines = [
        ProposalInline,
        IssueCommentInline,
        ReferenceInline,
        IssueAgendaItemInline,
        RankingInline,
    ]

    def proposal_count(self, instance):
        return instance.proposals.count()

    proposal_count.short_description = _("Proposals")

    def comment_count(self, instance):
        return instance.comments.count()

    comment_count.short_description = _("Comments")

    def reference_count(self, instance):
        return instance.references.count()

    reference_count.short_description = _("References")

    def meeting_count(self, instance):
        return instance.agenda_items.count()

    meeting_count.short_description = _("Meetings")


class IssueCommentAdmin(admin.ModelAdmin):
    list_display = (
        'issue',
        'community',
        'created_at',
        'created_by',
        'meeting',
        'active',
    )
    list_filter = (
        'issue__community',
        'meeting',
        'active',
    )
    search_fields = (
        'content',
    )
    date_hierarchy = 'created_at'

    def community(self, instance):
        return instance.issue.community

    community.admin_order_field = 'issue__community'
    community.short_description = _("Community")


class ReferenceAdmin(admin.ModelAdmin):
    list_display = (
        'issue',
        'community',
        'created_at',
        'created_by',
        'meeting',
        'active',
    )
    list_filter = (
        'issue__community',
        'meeting',
        'active',
    )
    search_fields = (
        'content',
    )
    date_hierarchy = 'created_at'

    def community(self, instance):
        return instance.issue.community

    community.admin_order_field = 'issue__community'
    community.short_description = _("Community")


class ProposalAdmin(admin.ModelAdmin):
    list_display = (
        'community',
        'issue',
        'type',
        'title',
        'status',
        'decided_at_meeting',
        'created_at',
        'active',
    )
    list_filter = (
        'status',
        'issue__community',
        'decided_at_meeting',
        'active',
    )
    search_fields = (
        'id',
        'title',
        'content',
    )
    list_display_links = (
        'community',
        'issue',
        'type',
        'title',
    )
    date_hierarchy = 'created_at'

    def community(self, instance):
        return instance.issue.community

    community.admin_order_field = 'issue__community'
    community.short_description = _("Community")


class ProposalCommentAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'created_by',
        'get_issue',
        'comment',
    )
    list_filter = (
        'created_at',
        'created_by',
        'comment',
    )
    search_fields = (
        'created_by',
    )
    date_hierarchy = 'created_at'

    def get_issue(self, instance):
        return instance.proposal.issue

    get_issue.short_description = _('Issue')


site.register(models.Issue, IssueAdmin)
site.register(models.Proposal, ProposalAdmin)
site.register(models.ProposalComment, ProposalCommentAdmin)


class ProposalVoteAdmin(admin.ModelAdmin):
    list_display = (
        'proposal',
        'user',
        'value'
    )

    list_filter = (
        'proposal',
        'user',
        'value'
    )
    list_display_links = (
        'proposal',
        'user',
        'value'
    )
    ordering = ['proposal', ]


site.register(models.ProposalVote, ProposalVoteAdmin)


class VoteResultAdmin(admin.ModelAdmin):
    list_display = (
        'meeting',
        'proposal',
        'community_members',
        'votes_pro',
        'votes_con',
    )

    ordering = ['proposal', ]


site.register(models.VoteResult, VoteResultAdmin)

site.register(models.IssueComment, IssueCommentAdmin)
site.register(models.Reference, ReferenceAdmin)


class ProposalVoteArgumentAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'created_by',
        'proposal_vote',
        'argument'
    )

    list_display_links = (
        'created_at',
        'created_by',
        'proposal_vote',
        'argument'
    )
    ordering = ['created_at', ]


site.register(models.ProposalVoteArgument, ProposalVoteArgumentAdmin)


class ProposalVoteArgumentRankingAdmin(admin.ModelAdmin):
    list_display = (
        'argument',
        'user',
        'value'
    )

    list_filter = (
        'user',
        'value'
    )
    list_display_links = (
        'argument',
        'user',
        'value'
    )


site.register(models.ProposalVoteArgumentRanking, ProposalVoteArgumentRankingAdmin)
