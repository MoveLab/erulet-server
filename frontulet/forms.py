from django import forms
from appulet.models import Route, Highlight, Reference, Box, InteractiveImage
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory


class InteractiveImageForm(forms.ModelForm):

    class Meta:
        model = InteractiveImage
        fields = ['image_file']

    def clean_image_file(self):
        uploaded_file = self.cleaned_data['image_file']
        if hasattr(uploaded_file, 'content_type'):
            print uploaded_file.content_type
            content_type = uploaded_file.content_type
            allowed_content_types = ['image/jpeg', 'image/jpg', 'image/png']
            if content_type in allowed_content_types:
                pass

            else:
                raise forms.ValidationError(_('filetype_not_supported'))
            return uploaded_file
        else:
            raise forms.ValidationError(_('error_no_file_selected'))


class BoxForm(forms.ModelForm):

    class Meta:
        model = Box
        fields = ['max_y', 'max_x', 'min_y', 'min_x', 'message_oc', 'message_es', 'message_ca', 'message_fr', 'message_en']


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class TranslateHighlightForm(forms.ModelForm):
    long_text_oc = forms.CharField(widget=forms.Textarea)
    long_text_es = forms.CharField(widget=forms.Textarea)
    long_text_ca = forms.CharField(widget=forms.Textarea)
    long_text_fr = forms.CharField(widget=forms.Textarea)
    long_text_en = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Highlight
        fields = ['name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en', 'long_text_oc', 'long_text_es', 'long_text_ca', 'long_text_fr', 'long_text_en']


class HighlightForm(forms.ModelForm):

    class Meta:
        model = Highlight
        fields = ['name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en', 'long_text_oc', 'long_text_es', 'long_text_ca', 'long_text_fr', 'long_text_en', 'type', 'media']

    def clean_media(self):
        uploaded_file = self.cleaned_data['media']
        if hasattr(uploaded_file, 'content_type'):
            print uploaded_file.content_type
            content_type = uploaded_file.content_type
            allowed_content_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'video/mp4', 'video/mebm', 'video/ogg']
            if content_type in allowed_content_types:
                pass

            else:
                raise forms.ValidationError(_('filetype_not_supported'))
            return uploaded_file


class ReferenceForm(forms.ModelForm):

    class Meta:
        model = Reference
        fields = ['name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en', 'html_file']

    def clean_html_file(self):
        uploaded_file = self.cleaned_data['html_file']
        if hasattr(uploaded_file, 'content_type'):
            print uploaded_file.content_type
            content_type = uploaded_file.content_type
            allowed_content_types = ['application/octet-stream', '.zip',   'application/zip']
            if content_type in allowed_content_types:
                pass
            else:
                raise forms.ValidationError(_('filetype_not_supported'))
            return uploaded_file
        else:
            raise forms.ValidationError(_('no_file_selected'))


class RouteForm(forms.ModelForm):

    class Meta:
        model = Route
        fields = ['name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en', 'short_description_oc', 'short_description_es', 'short_description_ca', 'short_description_fr', 'short_description_en', 'description_oc', 'description_es', 'description_ca', 'description_fr', 'description_en', 'gpx_track', 'gpx_waypoints', 'gpx_pois']

    def clean_gpx_file(self):
        uploaded_file = self.cleaned_data['gpx_track']
        print uploaded_file.content_type

        content_type = uploaded_file.content_type
        allowed_content_types = ['text/xml', 'application/octet-stream']
        if content_type in allowed_content_types:
            if uploaded_file._size > 2621440:
                raise forms.ValidationError(_('keep_filesize_under') % (filesizeformat(uploaded_file._size)))

        else:
            raise forms.ValidationError(_('filetype_not_supported'))

        return uploaded_file


class EditRouteForm(forms.ModelForm):

    class Meta:
        model = Route
        fields = ['name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en', 'short_description_oc', 'short_description_es', 'short_description_ca', 'short_description_fr', 'short_description_en', 'description_oc', 'description_es', 'description_ca', 'description_fr', 'description_en']


class OfficialRouteForm(forms.ModelForm):

    class Meta:
        model = Route
        fields = ['official', 'name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en',  'short_description_oc', 'short_description_es', 'short_description_ca', 'short_description_fr', 'short_description_en', 'description_oc', 'description_es', 'description_ca', 'description_fr', 'description_en', 'gpx_track', 'gpx_waypoints', 'gpx_pois']

    def clean_gpx_file(self):
        uploaded_file = self.cleaned_data['gpx_track']
        print uploaded_file.content_type

        content_type = uploaded_file.content_type
        allowed_content_types = ['text/xml', 'application/octet-stream']
        if content_type in allowed_content_types:
            if uploaded_file._size > 2621440:
                raise forms.ValidationError(_('keep_filesize_under') % (filesizeformat(uploaded_file._size)))

        else:
            raise forms.ValidationError(_('filetype_not_supported'))

        return uploaded_file


class EditOfficialRouteForm(forms.ModelForm):

    class Meta:
        model = Route
        fields = ['official', 'name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en', 'short_description_oc', 'short_description_es', 'short_description_ca', 'short_description_fr', 'short_description_en', 'description_oc', 'description_es', 'description_ca', 'description_fr', 'description_en']


class RegistrationForm(forms.ModelForm):
    error_messages = {
        'duplicate_username': _("username_already_exists"),
        'password_mismatch': _("passwords_no_match"),
    }
    username = forms.RegexField(label=_("username"), max_length=30, regex=r'^[\w.@+-]+$', error_messages={'invalid': _("value_only_letters_numbers_")})
    password1 = forms.CharField(label=_("choose_password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("confirm_password"), widget=forms.PasswordInput)
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