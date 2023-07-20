from django.contrib import admin
from .models import *

admin.site.register(Recipe)
admin.site.register(Rating)
admin.site.register(Comment)
admin.site.register(UserProfile)

# Register your models here.
