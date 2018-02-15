from django.urls import path

from issues import views

urlpatterns = [
    path('', views.IssueList.as_view(), name="issues"),
    path('create/', views.IssueCreateView.as_view(), name="issue_create"),
    path('upcoming-create/', views.IssueCreateView.as_view(upcoming=True),
         name="issue_create_upcoming"),
    path('<int:pk>/', views.IssueDetailView.as_view(), name="issue"),
    path('<int:pk>/edit/', views.IssueEditView.as_view(),
         name="issue_edit"),
    path('<int:pk>/edit-abstract/', views.IssueEditAbstractView.as_view(),
         name="issue_edit_abstract"),
    path('<int:pk>/set-length/', views.IssueSetLengthView.as_view(),
         name="issue_set_length"),
    path('<int:pk>/complete/', views.IssueCompleteView.as_view(),
         name="issue_complete"),
    path('<int:pk>/delete/', views.IssueDeleteView.as_view(),
         name="issue_delete"),
    path('<int:pk>/attach/', views.AttachmentCreateView.as_view(),
         name="add_attachment"),
    path('<int:issue_id>/remove-attachment/<int:pk>/',
         views.AttachmentDeleteView.as_view(),
         name="attachment_delete"),
    path('<int:issue_id>/download-attachment/<int:pk>/',
         views.AttachmentDownloadView.as_view(),
         name="attachment_download"),
    path('<int:issue_id>/create-proposal/', views.ProposalCreateView.as_view(),
         name="proposal_create"),
    path('<int:issue_id>/<int:pk>/',
         views.ProposalDetailView.as_view(), name="proposal"),
    path('<int:issue_id>/<int:pk>/edit/',
         views.ProposalEditView.as_view(), name="proposal_edit"),
    path('<int:issue_id>/<int:pk>/delete/',
         views.ProposalDeleteView.as_view(), name="proposal_delete"),
    path('<int:issue_id>/<int:pk>/task_completed/',
         views.ProposalCompletedTaskView.as_view(), name="task_completed"),
    path('<int:issue_id>/<int:pk>/edit-task/',
         views.ProposalEditTaskView.as_view(), name="proposal_edit_task"),
    path('delete-comment/<int:pk>/',
         views.IssueCommentDeleteView.as_view(), name="delete_issue_comment"),
    path('edit-comment/<int:pk>/',
         views.IssueCommentEditView.as_view(), name="edit_issue_comment"),
    path('delete-reference/<int:pk>/',
         views.ReferenceDeleteView.as_view(), name="delete_reference"),
    path('edit-reference/<int:pk>/',
         views.ReferenceEditView.as_view(), name="edit_reference"),
    path('vote/<int:pk>/',
         views.ProposalVoteView.as_view(), name="vote_on_proposal"),
    path('vote/<int:pk>/multi/',
         views.MultiProposalVoteView.as_view(), name="multi_votes_on_proposal"),
    path('argument_vote/<int:pk>/',
         views.ArgumentRankingVoteView.as_view(), name="vote_on_argument"),
    path('<int:issue_id>/<int:pk>/proposal_arguments/',
         views.ProposalArgumentsView.as_view(), name="proposal_arguments"),
    path('<int:issue_id>/<int:pk>/proposal_more_arguments/',
         views.ProposalMoreArgumentsView.as_view(), name="proposal_more_arguments"),
    path('<int:proposal_id>/proposal-comment-create/',
         views.ProposalCommentCreateView.as_view(), name="create_proposal_comment"),
    path('<int:vote_id>/vote-argument-create/',
         views.ProposalVoteArgumentCreateView.as_view(), name="create_vote_argument"),
    path('delete-proposal-comment/<int:pk>/',
         views.ProposalCommentDeleteView.as_view(), name="delete_proposal_comment"),
    path('edit-proposal-comment/<int:pk>/',
         views.ProposalCommentUpdateView.as_view(), name="edit_proposal_comment"),
    path('delete-vote-argument/<int:pk>/',
         views.ProposalVoteArgumentDeleteView.as_view(), name="delete_proposal_argument"),
    path('edit-vote-argument/<int:pk>/',
         views.ProposalVoteArgumentUpdateView.as_view(), name="edit_proposal_argument"),
    path('get-argument-value/<int:arg_id>/',
         views.get_argument_value, name="get_argument_value"),
    path('get-proposal-comment-value/<int:arg_id>/',
         views.get_proposal_comment_value, name="get_proposal_comment_value"),
    path('argument-up-down-vote/<int:pk>/',
         views.ArgumentRankingVoteView.as_view(), name="argument_up_down_vote"),
    path('vote_res_panel/<int:pk>/',
         views.VoteResultsView.as_view(), name="vote_results_panel"),
    path('<int:issue_id>/set_register_votes/<int:pk>/',
         views.ChangeBoardVoteStatusView.as_view(), name="set_register_votes"),
    path('autocomplete_tag/',
         views.AutoCompleteTagView.as_view(), name="autocomplete_tag"),
    path('assignments/',
         views.AssignmentsView.as_view(), name="assignments"),
    path('procedures/',
         views.ProceduresView.as_view(), name="procedures"),
]
