from django import forms

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class ReferenceUploadForm(forms.Form):
    person_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder':'Person name e.g. CEO'}))
    images = forms.FileField(widget=MultiFileInput(attrs={'multiple': True}))
