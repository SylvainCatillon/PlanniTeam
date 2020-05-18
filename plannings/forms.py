from django import forms

from plannings.models import Planning


class PlanningCreationForm(forms.ModelForm):
    # guests = forms.MultipleChoiceField(
    #     required=False,
    #     widget={forms.SelectMultiple(attrs={'hiden'})})

    class Meta:
        model = Planning
        widgets = {'creator': forms.HiddenInput(), }
        fields = ['name', 'protected', 'creator']
