# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render
from Accounts.models import Prod_Val

# Create your views here.
def index(request):
	if not request.user.is_superuser:
		return HttpResponse('No Access')
	store_owners = Prod_Val.objects.all()
	return render(request,'adminpanel/index.html',{'store_owners':store_owners})
