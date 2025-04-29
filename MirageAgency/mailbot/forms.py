from django import forms
from .models import Blacklist, GoldMan


class BlacklistForm(forms.ModelForm):
    class Meta:
        model = Blacklist
        fields = ['man_id']
        widgets = {
            'man_id': forms.NumberInput(attrs={'class': 'number_input'}),
        }

class GoldManForm(forms.ModelForm):
    class Meta:
        model = GoldMan
        fields = ['man_id']
        widgets = {
            'man_id': forms.NumberInput(attrs={'class': 'number_input'}),
        }