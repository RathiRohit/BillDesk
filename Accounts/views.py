from django.contrib import admin
from django.contrib import messages
from django.apps import apps
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.management import call_command
from importlib import import_module
from django.conf import settings
from django.core.urlresolvers import clear_url_caches
from django.shortcuts import render, redirect
from Accounts.forms import SignUpForm
from .models import Prod_Val, Profile
from django.db import models
import urllib
from datetime import datetime   
import urllib2
from django.utils.translation import ugettext as _


from django.contrib.auth.models import User
import json


def signup(request):
	if request.method == 'POST':
		form = SignUpForm (request.POST )
		if form.is_valid ():
			store_id = request.POST.get('store_id')
			store_pw = request.POST.get ('pass_wrd')
			store_owner = User.objects.filter(username=store_id).first()
			if store_owner is None or not store_owner.check_password(store_pw) :
				print 'Error'
				return render (request, 'Accounts/signup.html', {'form': form,'Error':'Store owner credentials failed !'})
			print 'No Error'
			user = form.save ()
			user.refresh_from_db ()  # load the profile instance created by the signal
			user.profile.full_name = form.cleaned_data.get ('full_name')
			user.profile.mob_number = form.cleaned_data.get ('mob_number')
			user.profile.email_id = form.cleaned_data.get ('email_id')
			user.email = user.profile.email_id
			user.profile.store_id=store_id
			user.save ()
			raw_password = form.cleaned_data.get ('password1')
			user = authenticate (username=user.username, password=raw_password)
			login (request, user)
			return redirect ('/DashBoard/')
		else:
			return render (request, 'Accounts/signup.html', {'form': form})
	else:
		form = SignUpForm ()
	return render (request, 'Accounts/signup.html', {'form': form})


def create_model(name, fields=None, app_label='', module='', options=None, admin_opts=None, createModel=True,
                 register=True):
    """
    Create specified model
    """
    name = str (name)

    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        pass

    if app_label:
        # app_label must be set using the Meta inner class
        setattr (Meta, 'managed', createModel)
        setattr (Meta, 'app_label', app_label)

    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.iteritems ():
            setattr (Meta, key, value)

    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta': Meta}

    # Add in any fields that were provided
    if fields:
        attrs.update (fields)

    # Create the class, which automatically triggers ModelBase processing
    model = type (name, (models.Model,), attrs)

    # Create an Admin class if admin options were provided
    
    if register and admin_opts is not None:
        class Admin (admin.ModelAdmin):
        	pass
        for key, value in admin_opts:
            setattr (Admin, key, value)
        admin.site.register (model, Admin)

    return model


def get_all_attr(n_model,Customer=None,Inventory=None,Billing=None):
    if n_model == 'Billing':
        fields = {
            'saletime': models.DateTimeField(default=datetime.now, blank=True),
            'Customer': models.ForeignKey(Customer,on_delete=models.CASCADE),
            'tot_price': models.IntegerField(default=0)
        }
        meta = {}
        app_label = 'DashBoard'
        return fields, meta, app_label

    elif n_model == 'Inventory':
        fields = {
            'id': models.AutoField (auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
            'i_name': models.CharField (max_length=100),
            'i_price': models.IntegerField (default=0),
            'gst_perc': models.IntegerField (default=0),
            'del_flag':models.BooleanField(default=True)
        }
        meta = {'ordering': ['i_name']}
        app_label = 'DashBoard'
        return fields, meta, app_label
    elif n_model == 'Customer':
        fields = {
            'id': models.AutoField (auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
            'c_name': models.CharField (max_length=100),
            'age_group': models.IntegerField (),
            'village': models.CharField (max_length=20),
            'phone': models.CharField (max_length=20),
            'gst_in': models.CharField(max_length=15,default=''),
            'del_flag':models.BooleanField(default=True)
        }
        meta = {'ordering': ['c_name']}
        app_label = 'DashBoard'
        return fields, meta, app_label
    elif n_model == 'Bill_Inven':
    	fields = {
            'Inventory': models.ForeignKey(Inventory,on_delete=models.CASCADE),
            'Billing':models.ForeignKey(Billing,on_delete=models.CASCADE),
            'count': models.IntegerField(default=0),
            'price':models.IntegerField(default=0)
        }
        meta = {}
        app_label = 'DashBoard'
        return fields, meta, app_label

def c_store_db(username):
	try:
		f, m, a = get_all_attr ('Inventory')
		Inven = create_model (username+'Inventory', fields=f, module=a + '.models', options=m, app_label=a, admin_opts={})
		f, m, a = get_all_attr ('Customer')
		Custo = create_model (username+'Customer', fields=f, module=a + '.models', options=m, app_label=a, admin_opts={})
		f, m, a = get_all_attr ('Billing',Customer=Custo)
		Bill = create_model (username+'Billing', fields=f, module=a + '.models', options=m, app_label=a, admin_opts={})
		f, m, a = get_all_attr ('Bill_Inven',Inventory=Inven,Billing=Bill)
		create_model (username+'Bill_Inven', fields=f, module=a + '.models', options=m, app_label=a, admin_opts={})
		
		call_command ('makemigrations')
		call_command ('migrate')
		reload (import_module (settings.ROOT_URLCONF))
		clear_url_caches ()
   	except Exception as e:
   		print '\n\n\tTable Not Created !!! due to ' + str(e)
   		return False
   	return True

def get_model(username,n_model):
	return apps.get_model('DashBoard',username+n_model)
	
def adminsignup(request):
    productkeyErrors = ''
    if request.method == 'POST':
        pk = request.POST['productkey']
        form = SignUpForm (request.POST)
        if form.is_valid ():
			if (len (pk) > 0):
			    try:
			        url = 'https://billdesk-auth.000webhostapp.com'
			        post_fields = {'pk': pk}
			        response = urllib2.Request (url, urllib.urlencode (post_fields).encode ())
			        j = json.loads (urllib2.urlopen (response).read ())
			        state = j['state']
			    except:
			        state = -1
			else:
			    state = 0;
			if state == -1:
			    productkeyErrors = 'Error in verifying Product Key, Try Again'
			elif state == 0:
			    productkeyErrors = 'Wrong Product Key'
			elif state == 1:
			    productkeyErrors = 'Key already registered'
			if state != 2:
				return render (request, 'Accounts/adminsignup.html',
			                   {'form': form, 'productkeyErrors': productkeyErrors})
			user = form.save ()
			user.refresh_from_db ()  # load the profile instance created by the signal
			user.profile.full_name = form.cleaned_data.get ('full_name')
			user.profile.mob_number = form.cleaned_data.get ('mob_number')
			user.profile.email_id = form.cleaned_data.get ('email_id')
			user.profile.Authority_Admin = 'checked'
			user.profile.Authority_Billing = 'checked'
			user.profile.Authority_Inventory = 'checked'
			user.profile.Authority_Customer = 'checked'
			user.profile.store_id = user.username
			user.save ()
			c_store_db(user.username)
			P_Val = Prod_Val(product_key=pk,Profile=user.profile,con_detail=user.profile.mob_number)
			P_Val.save()
			raw_password = form.cleaned_data.get ('password1')
			user = authenticate (username=user.username, password=raw_password)
			login (request, user)
			return redirect ('/DashBoard/')
    else:
        form = SignUpForm ()
    return render (request, 'Accounts/adminsignup.html', {'form': form, 'productkeyErrors': productkeyErrors})

def profile(request,username):
	user=User.objects.get(username=username)
	data=Profile.objects.get(user=user)
	return render(request,'Accounts/profile.html',{'data':data})

def profileUpdate(request):
	username=request.user.username
	user=User.objects.get(username=username)
	data=Profile.objects.get(user=user)
	data.full_name=request.POST.get('full_name')
	data.mob_number=request.POST.get('mob_number')
	data.email_id=request.POST.get('email_id')
	data.save()
	return redirect('Accounts:profile', username=request.user.username)


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('Your password was successfully updated!'))
            return redirect('Accounts:profile',username=request.user.username)
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'Accounts/change_password.html', {
        'form': form
    })