from django.db import models
from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	name = models.CharField(max_length=100)
	address = models.CharField(max_length=400,blank=True)
	title = models.CharField(max_length=100,default="Untitled")
	subtitle = models.CharField(max_length=300,default="Small default subtitle")
	slug = models.SlugField(max_length=250,blank=True)

	def __str__(self):
		return self.name 

class Materials(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	company = models.ForeignKey(Company,on_delete=models.CASCADE)
	name = models.CharField(max_length=300)
	sample_quantity = models.FloatField()
	sample_rate = models.FloatField()
	rate = models.FloatField()

	def __str__(self):
		return f"{self.name} | {self.company.name}"

class RefNo(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	ref_no = models.IntegerField()
	ssid = models.CharField(max_length=300)
	timestamp = models.DateTimeField(auto_now_add=True)
	company = models.ForeignKey(Company,on_delete=models.CASCADE)
	is_claimed = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.ref_no} | {self.company.name}"


class Order(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	ref_no = models.ForeignKey(RefNo,on_delete=models.CASCADE)
	material = models.ForeignKey(Materials,on_delete=models.CASCADE)
	quantity = models.FloatField()
	color = models.CharField(max_length=30)
	company=models.ForeignKey(Company,on_delete=models.CASCADE)

	def __str__(self):
		return f"{self.ref_no.ref_no} | {self.company.name}"

class DcMod(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	dc_no=models.IntegerField(default=1)
	ref_no = models.ForeignKey(RefNo,on_delete=models.CASCADE)
	ssid = models.CharField(max_length=300)
	company=models.ForeignKey(Company,on_delete=models.CASCADE)
	is_claimed = models.BooleanField(default=False)
	bill_no = models.IntegerField(blank = True,null = True)

	def __int__(self):
		return self.dc_no
	
class Extra(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	company = models.ForeignKey(Company,on_delete=models.CASCADE)
	bill_no = models.IntegerField()
	dc_no = models.IntegerField()	
	
	def __str__(self):
		return f"{self.dc_no} | {self.company}"

class Bill(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	timestamp = models.DateTimeField(auto_now_add = True)
	bill_no=models.IntegerField(default=1)
	company=models.ForeignKey(Company,on_delete=models.CASCADE)
	ssid=models.CharField(max_length=300)
	total = models.FloatField()
	gst = models.FloatField()
	amount = models.FloatField()

	def __str__(self):
		return f"{self.bill_no}"


