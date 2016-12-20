from django.forms import Form, FileField, ClearableFileInput, ChoiceField, CharField
from .models import Genre


class UploadForm(Form):
    choose_files = FileField(widget=ClearableFileInput(attrs={'multiple': True}))


class AddGenreForm(Form):
    genre = CharField(max_length=50)


class SelectGenre(Form):
    genre = ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super(SelectGenre, self).__init__(*args, **kwargs)
        name_choices = []
        if Genre.objects.count() > 0:
            name_choices = [(i.genre, i.genre) for i in Genre.objects.all().order_by('genre').distinct()]
        self.fields['genre'] = ChoiceField(choices=name_choices)


class RemoveGenreForm(Form):
    genre = ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super(RemoveGenreForm, self).__init__(*args, **kwargs)
        name_choices = []
        if Genre.objects.count() > 0:
            name_choices = [(i.genre, i.genre) for i in Genre.objects.all().order_by('genre').distinct()]
        self.fields['genre'] = ChoiceField(choices=name_choices)
