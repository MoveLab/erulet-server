from django import forms
from appulet.models import Route, Highlight, Reference, Box, InteractiveImage
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class InteractiveImageForm(forms.ModelForm):

    class Meta:
        model = InteractiveImage
        fields = ['image_file']


class BoxForm(forms.ModelForm):

    class Meta:
        model = Box
        fields = ['max_y', 'max_x', 'min_y', 'min_x', 'message']


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class HighlightForm(forms.ModelForm):

    class Meta:
        model = Highlight
        fields = ['name', 'long_text', 'type', 'media']

    def clean_media_file(self):
        uploaded_file = self.cleaned_data['media']
        if hasattr(uploaded_file, 'content_type'):
            print uploaded_file.content_type
            content_type = uploaded_file.content_type
            allowed_content_types = ['image', 'video']
            if content_type in allowed_content_types:
                pass

            else:
                raise forms.ValidationError(_('Filetype not supported.'))
            return uploaded_file
        else:
            raise forms.ValidationError(_('No file selected.'))


class ReferenceForm(forms.ModelForm):

    class Meta:
        model = Reference
        fields = ['name', 'html_file']

    def clean_html_file(self):
        uploaded_file = self.cleaned_data['html_file']
        if hasattr(uploaded_file, 'content_type'):
            print uploaded_file.content_type
            content_type = uploaded_file.content_type
            allowed_content_types = ['application/octet-stream', '.zip',   'application/zip']
            if content_type in allowed_content_types:
                pass
            else:
                raise forms.ValidationError(_('Filetype not supported.'))
            return uploaded_file
        else:
            raise forms.ValidationError(_('No file selected.'))


class RouteForm(forms.ModelForm):

    class Meta:
        model = Route
        fields = ['name', 'short_description', 'description', 'gpx_track', 'gpx_waypoints', 'gpx_pois']

    def clean_gpx_file(self):
        uploaded_file = self.cleaned_data['gpx_track']
        print uploaded_file.content_type

        content_type = uploaded_file.content_type
        allowed_content_types = ['text/xml', 'application/octet-stream']
        if content_type in allowed_content_types:
            if uploaded_file._size > 2621440:
                raise forms.ValidationError(_('Please keep filesize under 2.5 MB. Current filesize %s') % (filesizeformat(uploaded_file._size)))

        else:
            raise forms.ValidationError(_('Filetype not supported.'))

        return uploaded_file


class OfficialRouteForm(forms.ModelForm):

    class Meta:
        model = Route
        fields = ['official', 'name', 'short_description', 'description', 'gpx_track', 'gpx_waypoints', 'gpx_pois']

    def clean_gpx_file(self):
        uploaded_file = self.cleaned_data['gpx_track']
        print uploaded_file.content_type

        content_type = uploaded_file.content_type
        allowed_content_types = ['text/xml', 'application/octet-stream']
        if content_type in allowed_content_types:
            if uploaded_file._size > 2621440:
                raise forms.ValidationError(_('Please keep filesize under 2.5 MB. Current filesize %s') % (filesizeformat(uploaded_file._size)))

        else:
            raise forms.ValidationError(_('Filetype not supported.'))

        return uploaded_file


class RegistrationForm(forms.ModelForm):
    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^[\w.@+-]+$', error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    password1 = forms.CharField(label=_("Choose Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Confirm Password"), widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ("username",)

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(self.error_messages['password_mismatch'], code='password_mismatch',)
        return password2

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user