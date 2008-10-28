from django.contrib import admin

from email_change.models import EmailChange


class EmailChangeAdmin(admin.ModelAdmin):
	list_display = ('user', 'new_email_address')
	search_fields = ('new_email_address', 'user__first_name', 'user__last_name')


admin.site.register(EmailChange, EmailChangeAdmin)

