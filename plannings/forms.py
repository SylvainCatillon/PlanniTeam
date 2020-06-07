from django import forms

from plannings.models import Planning, Event


class PlanningCreationForm(forms.ModelForm):
    """Form for the Planning creation. Contains the fields name and protected
    with their base widgets, and the field creator as a hidden input."""

    class Meta:
        model = Planning
        fields = ['name', 'protected', 'creator']
        widgets = {'creator': forms.HiddenInput(), }
        labels = {'protected': "Restreindre l'accès au planning"}
        help_texts = {
            'protected': "Vous pouvez restreindre l'accès aux "
                         "emails sélectionnés, ou le laisser libre"
        }


class EventCreationForm(forms.ModelForm):
    """Form for the Event creation.
    Contains the fields description and address with their base widgets,
    and the fields date and time with date and time widgets."""
    class Meta:
        model = Event
        widgets = {
            'date': forms.DateInput(attrs={'placeholder': 'JJ/MM/AAAA'}),
            'time': forms.TimeInput(attrs={'placeholder': 'HH:MM'})
        }
        fields = ['date', 'time', 'description', 'address']


# Definition of an inlineformset to create events related to a planning
EventInlineFormSet = forms.inlineformset_factory(
    Planning, Event, form=EventCreationForm, extra=0)
