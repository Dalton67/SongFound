from django import forms


class InputForm(forms.Form):
    search = forms.CharField(label='Type some words', max_length=30)
