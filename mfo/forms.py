from django.forms import Form, FileField


class UploadForm(Form):
    uploaded_file = FileField()
