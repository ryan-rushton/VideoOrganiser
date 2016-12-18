from django.forms import Form, FileField, ClearableFileInput


class UploadForm(Form):
    uploaded_file = FileField(widget=ClearableFileInput(attrs={'multiple': True}))
