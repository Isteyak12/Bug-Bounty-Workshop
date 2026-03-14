from django import forms


class UploadForm(forms.Form):
    image = forms.ImageField()


class PresetForm(forms.Form):
    name = forms.CharField(max_length=100)
    dot_spacing = forms.IntegerField(initial=10, min_value=1)
    style = forms.ChoiceField(choices=[("classic", "Classic"), ("diamond", "Diamond"), ("line", "Line")])
    is_default = forms.BooleanField(required=False)


class PresetImportForm(forms.Form):
    json_data = forms.CharField(widget=forms.Textarea)


class BatchUploadForm(forms.Form):
    images = forms.FileField(widget=forms.ClearableFileInput(attrs={"allow_multiple_selected": True}))
    make_public = forms.BooleanField(required=False, label="Make all images public")
