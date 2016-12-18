from django.forms import Form, FileField, ClearableFileInput


class UploadForm(Form):
    uploaded_files = FileField(widget=ClearableFileInput(attrs={'multiple': True}))
