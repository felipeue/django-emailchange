from email_change.models import *
from django import forms
from django.utils.translation import ugettext as _

class EmailChangeForm(forms.ModelForm):
	class Meta:
		model = EmailChange
		fields = ('new_email_address',)
	def clean_new_email_address(self):
		addr = self.cleaned_data['new_email_address']
		if User.objects.filter(email__iexact=addr):
			raise forms.ValidationError(_(u'This email address is already in use. Please supply a different email address.'))
		return addr

