from django import forms

class BookingForm(forms.Form):
    hours = forms.IntegerField(label='Booking Duration (hours)', min_value=1, max_value=72)
    purpose = forms.CharField(
        label='Purpose', 
        max_length=255, 
        required= True, 
        widget=forms.Textarea(attrs={'rows': 5}))