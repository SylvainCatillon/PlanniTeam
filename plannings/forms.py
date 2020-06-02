from django import forms

from plannings.models import Planning, Event


class PlanningCreationForm(forms.ModelForm):
    # guests = forms.MultipleChoiceField(
    #     required=False,
    #     widget={forms.SelectMultiple(attrs={'hiden'})})

    class Meta:
        model = Planning
        widgets = {'creator': forms.HiddenInput(), }
        fields = ['name', 'protected', 'creator']


class EventCreationForm(forms.ModelForm):
    class Meta:
        model = Event
        widgets = {'date': forms.DateInput(attrs={'placeholder': 'AAAA-MM-JJ'}),
                   'time': forms.TimeInput(attrs={'placeholder': 'HH:MM'})}
        fields = ['date', 'time', 'description', 'address']


EventInlineFormSet = forms.inlineformset_factory(
    Planning, Event, form=EventCreationForm, extra=0)
