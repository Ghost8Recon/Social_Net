from django import forms

from .models import Gallery


class AlbumForm(forms.ModelForm):

    class Meta:
        model = Gallery
        fields = ['artist', 'album_title', 'genre', 'album_logo']