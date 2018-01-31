from django import forms
from django.conf import settings

from communities.models import Community, SendToOption, MeetingAttachment
from datetime import datetime, date, time
from django.utils.translation import ugettext_lazy as _
from ocd.formfields import HTMLArea, OCSplitDateTime, OCCheckboxSelectMultiple, OCTextInput, OCSplitDateTimeField
from haystack.forms import ModelSearchForm


class EditUpcomingMeetingForm(forms.ModelForm):
    upcoming_meeting_scheduled_at = OCSplitDateTimeField(
        label=_('Scheduled at'),
        widget=OCSplitDateTime(
            date_attrs={'type': 'text', 'class': 'form-control datepicker'},
            time_attrs={'type': 'time', 'class': 'form-control timepicker'},
            attrs={'class': 'form-control'}
        ),
        required=False)

    class Meta:
        model = Community

        fields = [
            'upcoming_meeting_title',
            # 'upcoming_meeting_location',
            'upcoming_meeting_scheduled_at',
            # 'voting_ends_at',
            'upcoming_meeting_comments',
        ]

        labels = {
            'upcoming_meeting_title': _('Title'),
            # 'upcoming_meeting_scheduled_at': _('Scheduled at'),
            # 'upcoming_meeting_location': _('Location'),
            'upcoming_meeting_comments': _('Background'),
        }

        widgets = {
            'upcoming_meeting_title': OCTextInput,
            # 'upcoming_meeting_scheduled_at': OCSplitDateTime(
            #     date_attrs={'type': 'date', 'class': 'form-control'},
            #     time_attrs={'type': 'time', 'class': 'form-control'},
            #     attrs={'class': 'form-control'}
            # ),
            # 'upcoming_meeting_location': OCTextInput,
            # 'voting_ends_at': OCSplitDateTime,
            'upcoming_meeting_comments': HTMLArea,
        }

    """
    removed this function as we don't include voting_end_time in the form any more.
    # ----------------------------------------------------------------------------
    def clean(self):
        #prevent voting end time from illegal values (past time,
        #time after meeting schedule)
        
        try:
            voting_ends_at = self.cleaned_data['voting_ends_at']
        except KeyError:
            voting_ends_at = None
        try:
            meeting_time = self.cleaned_data['upcoming_meeting_scheduled_at']
        except KeyError:
            meeting_time = None

        if voting_ends_at:
            if voting_ends_at <= timezone.now():
                raise forms.ValidationError(_("End voting time cannot be set to the past"))
            if meeting_time and voting_ends_at > meeting_time:
                raise forms.ValidationError(_("End voting time cannot be set to after the meeting time"))
        return self.cleaned_data
    """

    def save(self):
        c = super(EditUpcomingMeetingForm, self).save()
        c.voting_ends_at = datetime.combine(date(2025, 1, 1), time(12, 0, 0))
        c.save()
        return c


class PublishUpcomingMeetingForm(forms.ModelForm):
    send_to = forms.TypedChoiceField(label=_("Send to"), coerce=int,
                                     choices=SendToOption.choices,
                                     widget=forms.RadioSelect)

    class Meta:
        model = Community
        fields = []


class EditUpcomingMeetingSummaryForm(forms.ModelForm):
    class Meta:
        model = Community

        fields = (
            'upcoming_meeting_summary',
        )

        widgets = {
            'upcoming_meeting_summary': HTMLArea,
        }


class UpcomingMeetingParticipantsForm(forms.ModelForm):
    board = forms.MultipleChoiceField(widget=OCCheckboxSelectMultiple, required=False)

    class Meta:
        model = Community

        fields = (
            'upcoming_meeting_participants',
            'upcoming_meeting_guests',
        )

        widgets = {
            'upcoming_meeting_participants': OCCheckboxSelectMultiple,
            'upcoming_meeting_guests': forms.Textarea,
        }

    def __init__(self, *args, **kwargs):
        super(UpcomingMeetingParticipantsForm, self).__init__(*args, **kwargs)
        participants = self.instance.upcoming_meeting_participants.values_list(
            'id', flat=True)
        board_in = []
        board_choices = []
        for b in self.instance.get_board_members():
            board_choices.append((b.id, b.display_name,))
            if b.id in participants:
                board_in.append(b.id)
        self.fields['board'].choices = board_choices
        self.initial['board'] = board_in
        self.fields['upcoming_meeting_participants'].queryset = self.instance.get_members()
        self.fields['upcoming_meeting_participants'].label = ""


class CommunitySearchForm(ModelSearchForm):
    pass
    # def search(self):
    #     # First, store the SearchQuerySet received from other processing.
    #     sqs = super(DateRangeSearchForm, self).search()
    #
    #     if not self.is_valid():
    #         return self.no_query_found()
    #
    #     return sqs


class AddMeetingAttachmentBaseForm(forms.ModelForm):
    class Meta:
        model = MeetingAttachment
        fields = (
            'title',
            'file',
        )

        widgets = {
            'title': OCTextInput,
            # 'file': forms.ClearableFileInput(attrs={'multiple': True}),
        }

    def clean_file(self):
        file_obj = self.cleaned_data['file']

        if len(file_obj.name.split('.')) == 1:
            raise forms.ValidationError(_("File type is not allowed!"))

        if file_obj.name.split('.')[-1].lower() not in settings.UPLOAD_ALLOWED_EXTS:
            raise forms.ValidationError(_("File type is not allowed!"))

        return file_obj

    def clean_title(self):
        title = self.cleaned_data['title']

        if len(title.strip()) == 0:
            raise forms.ValidationError(_("Title cannot be empty"))

        return title


class AddMeetingAttachmentForm(AddMeetingAttachmentBaseForm):
    submit_button_text = _('Upload')
