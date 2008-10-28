from django.contrib.auth.decorators import login_required
from email_change.models import *
from email_change.forms import *
from django.views.generic.simple import direct_to_template
from django.db import transaction
from django.utils.http import urlquote
from django.http import HttpResponseRedirect

@transaction.commit_on_success
def change_request(request, activation_key=None, raise404=False):
	if activation_key:
		user = EmailChange.objects.change_email(activation_key)
		return direct_to_template(request, 'registration/email_change_done.html', dict(modified_user=user))

	if not request.user.is_authenticated():
		path = urlquote(request.get_full_path())
		return HttpResponseRedirect(settings.LOGIN_URL + '?next=' + path)
	form = EmailChangeForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		new_email_address = form.cleaned_data['new_email_address']
		ec = EmailChange.objects.create_email_change(user=request.user, new_email_address=new_email_address)
		if ec:
			ec.save()
			return direct_to_template(request, 'registration/email_change_confirm.html', dict(email=ec.new_email_address))
		# TODO what can go wrong?
	return direct_to_template(request, 'registration/email_change_form.html', dict(form=form))
