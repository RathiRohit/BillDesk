# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
import json, datetime, calendar
from .models import Customer
from Accounts.models import Profile,Prod_Val
from . import send
from django.core.mail import send_mail,EmailMessage
from django.db.models import Sum
from Accounts.views import c_store_db,create_model,get_all_attr,get_model
from django.db.models.functions import TruncDay, TruncMonth, TruncYear

# Create your views here.
@login_required(login_url='/Accounts/login/')
def index(request):
	if request.user.is_superuser:
		return redirect ('/adminpanel/')
	s_id = request.user.profile.store_id
	all_accounts = Profile.objects.filter(store_id=s_id)

	Inventory = get_model(s_id,'Inventory')
	inventories = Inventory.objects.all()
	if request.user.is_authenticated and request.user.is_active :
		permissions = {'Admin':request.user.profile.Authority_Admin,'Customer':request.user.profile.Authority_Customer, 'Billing':request.user.profile.Authority_Billing,'Inventory':request.user.profile.Authority_AddInventory,'Inven_change':request.user.username==s_id}
	else :
		permissions = {'Admin':'unchecked','Customer':'unchecked', 'Billing':'unchecked','Inventory':'unchecked','Inven_change':request.user.username==s_id}
	return render(request,'Dash.html',{'all_accounts':all_accounts,'inventories':inventories,'permissions':permissions})

@login_required(login_url='/Accounts/login/')
def confirm(request,w_id):
	account = get_object_or_404(Profile,id=w_id)
	if account.store_id == account.user.username :
		return HttpResponse("fail")
	if request.POST.get('inven',None) :
		account.Authority_AddInventory = 'checked'
	else:
		account.Authority_AddInventory = ''
	
	if request.POST.get('admin',None) :
		account.Authority_Admin = 'checked'
	else:
		account.Authority_Admin = ''
	
	if request.POST.get('custo',None) :
		account.Authority_Customer = 'checked'
	else:
		account.Authority_Customer = ''
	
	if request.POST.get('bill',None)  :
		account.Authority_Billing = 'checked'
	else:
		account.Authority_Billing = ''
	account.save()
	return HttpResponse('save')

@login_required(login_url='/Accounts/login/')
def autocompleteinven(request):
	store_id = request.user.profile.store_id
	Inventory = get_model(store_id,'Inventory')

	text = request.GET.get('term', '')
	results = Inventory.objects.filter(i_name__contains = text)
	res = []
	for inven in results:
		drug_json = {}
		drug_json['id'] = inven.id
		drug_json['label'] = inven.i_name + " Rs. " + str(inven.i_price)
		drug_json['value'] = inven.i_name
		res.append(drug_json)
	data = json.dumps(res)

	mimetype = 'application/json'
	return HttpResponse(data, mimetype)


@login_required(login_url='/Accounts/login/')
def autocompletecusto(request):
	text = request.GET.get('term', '')
	store_id = request.user.profile.store_id
	Customer = get_model(store_id,'Customer')
	
	results = Customer.objects.filter(c_name__contains = text)
	res = []
	for custo in results:
		drug_json = {}
		drug_json['id'] = custo.id
		drug_json['label'] = custo.c_name + " from : " + custo.village
		drug_json['value'] = custo.c_name
		res.append(drug_json)
	data = json.dumps(res)

	mimetype = 'application/json'
	return HttpResponse(data, mimetype)


@login_required(login_url='/Accounts/login/')
def add(request):
	store_id = request.user.profile.store_id
	Inventory = get_model(store_id,'Inventory')
	
	inven = request.POST.get('inven')
	cnt = request.POST.get('count')
	item = Inventory.objects.filter(i_name=inven).first()
	if item is None:
		return HttpResponse("fail")
	else:
		return HttpResponse(item.i_price)

@login_required(login_url='/Accounts/login/')
def addinven(request):
	store_id = request.user.profile.store_id
	Inventory = get_model(store_id,'Inventory')
	inven = request.POST.get('inven')
	i_price = request.POST.get('price')
	if inven == '' or inven == None or i_price == '' or i_price == None :
		return HttpResponse('fail')
	if Inventory.objects.filter(i_name=inven).first() is None:
		inven = Inventory(i_name=inven,i_price=i_price)
		inven.save()
		inventories = Inventory.objects.all()
		return HttpResponse(inven.id,{'inventories':inventories})
	else:
		return HttpResponse('fail')

@login_required(login_url='/Accounts/login/')
def placeorder(request):
	l = request.POST.get('List')
	c_n = request.POST.get('customername')
	tot_cost = request.POST.get('tot_cost')
	print tot_cost
	if c_n == '':
		c_n = 'guest'
	store_id = request.user.profile.store_id
	Custom = get_model(store_id,'Customer')
	Invent = get_model(store_id,'Inventory')
	Billing = get_model(store_id,'Billing')
	Bill_Inven = get_model(store_id,'Bill_Inven')
	custo = Custom.objects.get(c_name=c_n)
	
	print '1'+str(datetime.datetime.now()),custo.c_name,Billing,Custom.objects.all()
	Bill = Billing.objects.create(Customer=custo,tot_price=tot_cost)
	print '2'
	Bill.save()
	print 'Bill Saved'
	total = 0
	s = ''
	s += '-----------------------BILLDESK-----------------------\n'
	s += 'Date : \t\t\t\t' + str(datetime.datetime.now().replace(microsecond = 0))+'\n'
	s += '------------------------------------------------------\n'
	s += '%-10s %10s %10s %10s' % ('NAME','QTY','RATE','AMT') + '\n'
	items = json.loads(l)
	for i in items:
		s+= '%-10s %10s %10s %10s' % (i['_i_name'] ,str(i['_i_count']),str(i['_i_price']),str(i['_i_tot_price']))+'\n'
		inven = Invent.objects.get(i_name=i['_i_name'])
		record = Bill_Inven(Inventory=inven,Billing=Bill,count=i['_i_count'],price=i['_i_tot_price'])
		record.save()
		total += int(i['_i_tot_price'])

	s += '------------------------------------------------------\n'
	s += 'TOTAL : \t\t\t\t' + str(total)+"\n"
	s += '\t\tTHANK YOU VISIT AGAIN\n'
	s += '------------------------------------------------------\n'
	
	email = 'onkarsathe27@gmail.com'
	#send_mail('Bill','','programtowin@gmail.com',[email],fail_silently=False,html_message='<pre>'+s+'</pre>')
	return HttpResponse('success')

@login_required(login_url='/Accounts/login/')
def register(request):
	print(request.POST.get('customername'))
	custModel = get_model(request.user.profile.store_id, 'Customer')
	newCust = custModel(c_name=request.POST.get('customername'), village=request.POST.get('customervillage'), age_group=request.POST.get('customerage'), phone=request.POST.get('customerphone'))
	newCust.save()
	return HttpResponse('success')

@login_required(login_url='/Accounts/login/')
def modify(request):
	i_id = request.POST.get('id')
	f_id = int(request.POST.get('f_id'))	
	store_id = request.user.profile.store_id
	Inventory = get_model(store_id,'Inventory')
	if f_id == 1:
		i_name = str(request.POST.get('field'))
		inven = Inventory.objects.get(id=i_id)
		inven.i_name=i_name
		inven.save()
	elif f_id == 2:
		i_price = request.POST.get('field')
		inven = Inventory.objects.get(id=i_id)
		inven.i_price=int(i_price)
		inven.save()
	elif f_id == 3:
		igst = request.POST.get('field')
		inven = Inventory.objects.get(id=i_id)
		inven.gst_perc=str(igst)
		inven.save()
	return HttpResponse("success")


def test(request):

	return HttpResponse("success")	
	username = 'SAMR'
	for i in Prod_Val.objects.all():
		user = User.objects.get(username=i.Profile.user.username)
		c_store_db(user.username)
	
	custo = get_model(username,'Customer')
	print custo.objects.count()

	inven = get_model(username,'Inventory')
	print inven.objects.count()

	Bill = get_model(username,'Billing')
	print Bill.objects.count()

	Bill_inven = get_model(username,'Bill_Inven')
	print Bill_inven.objects.count()

@login_required(login_url='/Accounts/login/')
def changedata(request):
	chartType = request.POST.get('chartType')
	timeSpan = request.POST.get('timeSpan')
	response_data = {}
	response_data['chartType'] = chartType
	response_data['timeSpan'] = timeSpan
	startdate, enddate = get_dates(timeSpan)
	response_data['startdate'] = str(startdate)
	response_data['enddate'] = str(enddate)
	if chartType=='Client':
		billModel = get_model(request.user.profile.store_id, 'Billing')
		qs = billModel.objects.filter(saletime__range=(startdate, enddate)).values('Customer__c_name').annotate(Sum('tot_price'))
		response_data['values[]'] = list(qs.values_list('tot_price__sum', flat=True))
		response_data['labels[]'] = list(qs.values_list('Customer__c_name', flat=True))
	elif chartType=='Product':
		invModel = get_model(request.user.profile.store_id, 'Bill_Inven')
		qs = invModel.objects.filter(Billing__saletime__range=(startdate, enddate)).values('Inventory__i_name').annotate(Sum('price'))
		response_data['values[]'] = list(qs.values_list('price__sum', flat=True))
		response_data['labels[]'] = list(qs.values_list('Inventory__i_name', flat=True))
	elif chartType=='Line':
		billModel = get_model(request.user.profile.store_id, 'Billing')
		if timeSpan=='Daily':
			qs = billModel.objects.annotate(day=TruncDay('saletime')).values('day').annotate(Sum('tot_price'))
			response_data['values[]'] = list(qs.values_list('tot_price__sum', flat=True))
			response_data['labels[]'] = [d.strftime('%d/%m/%Y') for d in list(qs.values_list('day', flat=True))]
		elif timeSpan=='Monthly':
			qs = billModel.objects.annotate(month=TruncMonth('saletime')).values('month').annotate(Sum('tot_price'))
			response_data['values[]'] = list(qs.values_list('tot_price__sum', flat=True))
			response_data['labels[]'] = [d.strftime('%d/%m/%Y') for d in list(qs.values_list('month', flat=True))]
		elif timeSpan=='Yearly':
			qs = billModel.objects.annotate(year=TruncYear('saletime')).values('year').annotate(Sum('tot_price'))
			response_data['values[]'] = list(qs.values_list('tot_price__sum', flat=True))
			response_data['labels[]'] = [d.strftime('%d/%m/%Y') for d in list(qs.values_list('year', flat=True))]
	return JsonResponse(response_data)
	
#Function to get start & end date
def get_dates(timeSpan):
	if(timeSpan=='This Week'):
		today = datetime.date.today()
		startdate = today - datetime.timedelta(days=today.weekday())
		enddate = startdate + datetime.timedelta(days=7)	#7 instead of 6 for __range
	elif(timeSpan=='Last Week'):
		today = datetime.date.today()
		today = today - datetime.timedelta(days=7)
		startdate = today - datetime.timedelta(days=today.weekday())
		enddate = startdate + datetime.timedelta(days=7)	#7 instead of 6 for __range
	elif(timeSpan=='This Month'):
		today = datetime.date.today()
		startdate = today - datetime.timedelta(days=(today.day-1))
		enddate = startdate + datetime.timedelta(days=(calendar.monthrange(startdate.year, startdate.month)[1]))
	elif(timeSpan=='Last Month'):
		today = datetime.date.today()
		enddate = today - datetime.timedelta(days=(today.day))
		startdate = enddate - datetime.timedelta(days=(enddate.day-1))
	elif(timeSpan=='This Year'):
		today = datetime.date.today()
		startdate = datetime.datetime.strptime('01/01/'+str(today.year), '%d/%m/%Y').date()
		enddate = startdate + datetime.timedelta(days=365)
		if calendar.isleap(startdate.year):
			enddate = enddate + datetime.timedelta(days=1)
	elif(timeSpan=='Last Year'):
		today = datetime.date.today()
		startdate = datetime.datetime.strptime('01/01/'+str(today.year-1), '%d/%m/%Y').date()
		enddate = startdate + datetime.timedelta(days=365)
		if calendar.isleap(startdate.year):
			enddate = enddate + datetime.timedelta(days=1)
	else:
		startdate = '';
		enddate = '';
	return startdate,enddate