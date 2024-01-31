from .models import Comment
from django import forms

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',) # 혹은 exclude('post','author','create_at')처럼 여러개를 제외할때 exclude 사용 가능