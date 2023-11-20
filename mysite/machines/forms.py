from django import forms
from .models import Notepad
from tinymce.widgets import TinyMCE

class BookingForm(forms.Form):
    days = forms.IntegerField(
        label='',
        min_value=1,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Days', 'class': 'watermark'})
    )
    hours = forms.IntegerField(
        label='',
        min_value=1,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Hours', 'class': 'watermark'})
    )
    minutes = forms.IntegerField(
        label='',
        min_value=1,
        max_value=59,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Minutes', 'class': 'watermark'})
    )
    purpose = forms.CharField(
        label='',
        max_length=255,
        required=True,
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Purpose', 'class': 'watermark'})
    )
    

    def clean(self):
        cleaned_data = super().clean()
        days = cleaned_data.get('days', 0)
        hours = cleaned_data.get('hours', 0)
        minutes = cleaned_data.get('minutes', 0)

        # Ensure at least one field (days, hours, minutes) is provided
        if not any([days, hours, minutes]):
            raise forms.ValidationError('Please provide booking duration in days, hours, or minutes.')


class NotepadForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    class Meta:
        model = Notepad
        fields = ['content']