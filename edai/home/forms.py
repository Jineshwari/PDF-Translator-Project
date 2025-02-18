# forms.py
from django import forms

class DictionaryForm(forms.Form):
    dictionary_name = forms.CharField(max_length=100)
    word_pairs = forms.JSONField()  # To hold word pairs as a JSON object
