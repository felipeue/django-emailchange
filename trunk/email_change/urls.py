from django.conf.urls.defaults import *
urlpatterns = patterns('',
                       # Activation keys get matched by \w+ instead of the more specific
                       # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
                       # that way it can return a sensible "invalid key" message instead of a
                       # confusing 404.
                       url(r'^email_change/confirm/(?P<activation_key>\w+)/',
                           'email_change.views.change_request',
                           name='email_change_confirm'),
                       url(r'^email_change/$',
                           'email_change.views.change_request',
                           name='email_change_form'),
                       )
