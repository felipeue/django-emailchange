from django import forms
from django.contrib.auth.models import User, AnonymousUser
from django.db import models, connection, IntegrityError
from django.http import Http404
from django.conf import settings
from django.utils.encoding import smart_str
from django.db.models import Q
import datetime
import random
import sha
from django.contrib.auth.models import User 
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

class EmailChangeManager(models.Manager):
	def change_email(self, activation_key):
		"""
		Validate an activation key and change the corresponding
		``User`` if valid.

		If the key is valid and has not expired, return the ``User``
		after activating.

		If the key is not valid or has expired, return ``None``.

		If the key is valid but the ``User`` is already active,
		return ``None``.

		After successful email change the activation record is deleted.
		"""
		try:
			email_change = self.model.objects.get(activation_key=activation_key)
			expiration_date = datetime.timedelta(days=settings.EMAILCHANGE_ACTIVATION_DAYS)
			if email_change.requested_at + expiration_date < datetime.datetime.now():
				email_change.delete()
				raise EmailChange.DoesNotExist
			user = User.objects.get(pk=email_change.user_id)
			user.email = email_change.new_email_address
			user.save()
			email_change.delete()
			return user
		except EmailChange.DoesNotExist:
			return None

	def create_email_change(self, user, new_email_address, send_email=True):
		"""
		Generates an ``EmailChange`` and email its activation key to the new
		email address, returning the ``User``.

		The email changing

		To disable the email, call with ``send_email=False``.

		``user``
			The ``User`` who wants to change email address.
		``new_email_address``
			The requested new email address
		"""

		try:
			activation_key = sha.new(str(random.random()) + smart_str(new_email_address))
			ec = EmailChange.objects.filter(Q(user=user) or Q(new_email_address=new_email_address))
			if len(ec):
				ec = ec[0]
			else:
				ec = EmailChange(user=user, new_email_address=new_email_address)
			ec.activation_key=activation_key.hexdigest()
			ec.new_email_address = new_email_address
			ec.save()
		except IntegrityError:
			return None

		if send_email:
			from django.core.mail import send_mail
			current_site = Site.objects.get_current()

			subject = render_to_string('registration/email_change_subject.txt',
				{ 'site': current_site })
			# Email subject *must not* contain newlines
			subject = ' '.join(subject.splitlines())

			message = render_to_string('registration/email_change_email.txt',
				{ 'activation_key': ec.activation_key,
					'site': current_site })

			send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [ec.new_email_address]) 
		return ec

class EmailChange(models.Model):
	new_email_address = models.EmailField(_(u'new e-mail address'), help_text=_(u'Your old email address will be used until you verify your new one.'))
	user = models.ForeignKey(User, unique=True)
	requested_at = models.DateTimeField(default=datetime.datetime.now())
	activation_key = models.CharField(max_length=40, unique=True, db_index=True)
	objects = EmailChangeManager()
