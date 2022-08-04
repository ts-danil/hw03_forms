from django.forms import ModelForm, Textarea, Select
from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        widgets = {
            "text": Textarea(attrs={
                'class': 'form-control',
                'cols': '40',
                'rows': '10'
            }),
            "group": Select(attrs={
                'class': 'form-control'
            })
        }
