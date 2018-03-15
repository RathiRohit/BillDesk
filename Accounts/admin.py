from django.contrib import admin

# Register your models here.
from .models import Profile,Prod_Val

admin.site.register(Profile),

admin.site.register(Prod_Val),