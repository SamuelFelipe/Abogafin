from django.contrib import admin
from .models import *


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(BlogCalification)
admin.site.register(BlogComment)
admin.site.register(Responce)
