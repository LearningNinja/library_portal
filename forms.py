from django import forms
from .models import Post
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime
from pagedown.widgets import PagedownWidget

class RenewBookForm(forms.Form):
    renew_date = forms.DateField(help_text = "Enter a date between now and 4 weeks (default is 3 weeks)",widget=forms.SelectDateWidget)

    # clean_field is the default name of a function used for custom validation of that field
    def clean_renew_date(self):
        data = self.cleaned_data['renew_date']         # this is the data after default django basic form validations

        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Check date is in range librarian allowed to change (+4 weeks).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data

class CreatePostForm(forms.ModelForm):

    title = forms.CharField(widget=PagedownWidget)     # enables the django pagedown functionality
    content = forms.CharField(widget=PagedownWidget)

    class Meta:
        model = Post
        fields = ['title','content']



