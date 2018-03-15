# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Inventory,Customer
from Accounts.views import create_model,get_all_attr

# Register your models here.
admin.site.register(Inventory),

admin.site.register(Customer),

from Accounts.models import Prod_Val

All_Store = Prod_Val.objects.all()

for store in All_Store :
	fi , mi, ai = get_all_attr('Inventory')
	Inven = create_model(store.Profile.user.username+'Inventory',fields=fi,module=ai+'.models',options = mi,app_label=ai,admin_opts={},createModel=False)
	
	fc , mc, ac = get_all_attr('Customer')
	Custo = create_model(store.Profile.user.username+'Customer',fields=fc,module=ac+'.models',options = mc,app_label=ac,admin_opts={},createModel=False)
	
	fb , mb, ab = get_all_attr('Billing',Customer=Custo)
	Bill = create_model(store.Profile.user.username+'Billing',fields=fb,module=ab+'.models',options = mb,app_label=ab,admin_opts={},createModel=False)
	
	fci , mci, aci = get_all_attr('Bill_Inven',Inventory=Inven,Billing=Bill)
	model = create_model(store.Profile.user.username+'Bill_Inven',fields=fci,module=aci+'.models',options = mci,app_label=aci,admin_opts={},createModel=False)
	
	print store.Profile.user.username+' loaded'
