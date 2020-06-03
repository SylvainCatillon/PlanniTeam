from django import forms

from plannings.models import Planning, Event


class PlanningCreationForm(forms.ModelForm):
    # guests = forms.MultipleChoiceField(
    #     required=False,
    #     widget={forms.SelectMultiple(attrs={'hiden'})})

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
    class Meta:
        model = Event
        widgets = {
            'date': forms.DateInput(attrs={'placeholder': 'JJ/MM/AAAA'}),
            'time': forms.TimeInput(attrs={'placeholder': 'HH:MM'})
        }
        fields = ['date', 'time', 'description', 'address']


EventInlineFormSet = forms.inlineformset_factory(
    Planning, Event, form=EventCreationForm, extra=0)
