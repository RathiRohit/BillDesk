from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	full_name = models.CharField(max_length=500, blank=False)
	mob_number = models.CharField(max_length=15, blank=False)
	email_id = models.EmailField(max_length=254, null=True, blank=True)
	Authority_AddInventory = models.CharField(max_length=100,default='unchecked')
	Authority_Billing = models.CharField(max_length=100,default='unchecked')
	Authority_Admin = models.CharField(max_length=100,default='unchecked')
	Authority_Customer = models.CharField(max_length=100,default='unchecked')
	store_id = models.CharField(max_length=100,default='')

	def __str__(self):
		return self.user.username+" "+self.Authority_AddInventory+" "+self.Authority_Billing

class Prod_Val(models.Model):
	product_key = models.CharField(max_length=20)
	Profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
	time_rem = models.IntegerField(default=0)
	con_detail = models.CharField(max_length=10)
	is_active = models.BooleanField(default=False)
	gst_in = models.CharField(max_length=15,default='')

	def __str__(self):
		return self.Profile.user.username + " " + self.product_key+" " + str(self.time_rem)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
	
	
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()
