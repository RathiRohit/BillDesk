# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
# Create your models here.

class Inventory(models.Model):
	i_name = models.CharField(max_length=100)
	i_price = models.IntegerField(default=0)

	def __str__(self):
		return self.i_name + " " +str(self.i_price)

	class Meta:
			ordering = ['i_name']

class Customer(models.Model):
	c_name = models.CharField(max_length=100)
	age_group = models.IntegerField()
	village = models.CharField(max_length=20)
	fb_profile = models.CharField(default='',max_length=100)
	phone = models.CharField(max_length=10)
	def __str__(self):
		return self.c_name + " "+str(self.age_group)+" "+self.village

	class Meta:
			ordering = ['c_name']
