from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from lawyer_user.models import *
from .User import User


class UserAdmin(DefaultUserAdmin):
    fieldsets = (
            (None, {'fields': ('first_name', 'last_name', 'cel', 'tel',
                    'doc_type', 'doc_number', 'email', 'city', 'account_type'
                    )}),
            )
    list_display = ('names', 'surnames', 'email', 'verificated')
    search_fields = ('email', 'names', 'surnames')
    add_fieldsets = (
        (None, {
                'classes': ('wide',),
                'fields': ('email', 'first_name', 'last_name', 'cel', 'tel',
                           'doc_type', 'doc_number', 'city', 'account_type',
                           'password1', 'password2'),
                }
        ),
    )
    ordering = ('email',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_postulations', 'max_active_cases', 'price')


@admin.register(Bufete)
class BufeteAdmin(admin.ModelAdmin):
    list_display = ('name', 'legal_representative')


admin.site.register(Lawyer)
admin.site.register(UserCalification)
admin.site.register(BufeteCalification)
admin.site.register(Tag)
admin.site.register(Case)
admin.site.register(Interested)
