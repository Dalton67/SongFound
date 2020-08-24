from django import forms


class SongForm(forms.Form):
    user_song = forms.CharField(widget=forms.TextInput(), label='Song', max_length=100)