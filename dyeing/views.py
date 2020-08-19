from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from dyeing.models import *
from django.contrib.auth import authenticate,login,logout
import hashlib
from datetime import datetime
import json
from django.db.models import Max
from django.http import HttpResponse
from django.views.generic import View
from .utils import render_to_pdf 
from django.template.loader import get_template
from django import template
register = template.Library()

def home(request):
	return render(request,"home.html")

def owner_signup(request):
	if request.method == "POST":
		full_name=request.POST["full_name"]
		username=request.POST["username"]
		email=request.POST["email"]
		password=request.POST["password"]

		first_name=full_name.split()[0]
		last_name=" ".join(full_name.split()[1:])

		user = User.objects.create_user(first_name=first_name,
										last_name=last_name,
										username=username,
										email=email,
										password=password)
		

		login(request,user)
		return redirect("/dashboard/")			
	return render(request,"signup.html")

def owner_signin(request):
	if request.method == "POST":
		username=request.POST["username"]
		password=request.POST["password"]

		user=authenticate(request,username=username,password=password)

		if user is not None:
			login(request,user)
			return redirect("/dashboard/")

	return render(request,"signin.html")


def dashboard(request):
	#stores=Store.objects.filter(owner=request.user)
	bills = Bill.objects.filter(user = request.user)

	labels = []
	data = []
	total = 0
	for bill in bills:
		date = str(bill.timestamp.date())
		total += bill.amount

		if date not in labels:
			labels.append(date)
			data.append(total)
		else:
			index = labels.index(date)
			data[index] += total

		print(data)
		print(total)

	return render(request,"dashboard.html",{"labels":json.dumps(labels),"data":data})


def create_company(request):
	if request.method == "POST" and request.user.is_authenticated:
		print("hii")
		name=request.POST["name"]
		address=request.POST["address"]
		subtitle=request.POST["subtitle"]
		slug = "-".join(name.lower().split())
		user=request.user
		company=Company.objects.create(name=name,slug=slug,address=address,subtitle=subtitle,user=request.user)

		return redirect("/company-page/")
	return redirect("/dashboard/")

def company_page(request):
	company= Company.objects.filter(user=request.user)
	materials=Materials.objects.filter(company=company,user = request.user)

	return render(request,"company_dash.html",{"company":company,"materials":materials})

def rate_page(request,company_id):
	company=Company.objects.get(id=company_id,user = request.user)
	materials=Materials.objects.filter(company=company,user = request.user)
	return render(request,"rate_page.html",{"company":company,"materials":materials})

def create_material(request,company_id):
	company=Company.objects.get(id=company_id,user = request.user)

	if request.method=="POST":
		name=request.POST["name"]
		sample_quantity=request.POST["sample_quantity"]
		sample_rate=request.POST["sample_rate"]
		rate=request.POST["rate"]

		material=Materials.objects.create(
			user = request.user,
			company=company,
			name=name,
			sample_quantity=sample_quantity,
			rate=rate,
			sample_rate=sample_rate,
			)
		return redirect(f"/rate-page/{company.id}/")


def remove_material(request,material_id):
	materials = Materials.objects.get(pk=material_id)
	company = materials.company
	materials.delete()
	return redirect(f"/rate-page/{company.id}")

def edit_material(request,material_id):
	material=Materials.objects.get(pk=material_id)
	company = material.company
	if request.method=="POST":
		name=request.POST["name"]
		sample_quantity=request.POST["sample_quantity"]
		sample_rate=request.POST["sample_rate"]
		rate=request.POST["rate"]

		material.name=name
		material.sample_quantity=sample_quantity
		material.sample_rate=sample_rate
		material.rate=rate
		material.save()
		return redirect(f"/rate-page/{company.id}/")

def order_page(request,company_slug):
	company=Company.objects.get(slug=company_slug,user = request.user)
	ssid = request.session.session_key
	

	ref_no = RefNo.objects.filter(company=company,user=request.user).order_by('-ref_no')
	

	return render(request,"order_page.html",{"company":company,"ref_no":ref_no})


def add_ref(request,company_slug):
	company = Company.objects.get(slug=company_slug,user=request.user)
	materials = Materials.objects.filter(company=company,user=request.user)
	ssid = request.session.session_key
	
	if request.method == "POST":
		ref_no = request.POST["ref_no"]

		if not RefNo.objects.filter(ssid=ssid,company=company,ref_no=ref_no,user =request.user).exists():
			ref_no=RefNo.objects.create(ssid=ssid,company=company,ref_no=ref_no,user=request.user)

			return render(request,"add_ord.html",{"company":company,"ref_no":ref_no,"materials":materials})

	return redirect(f"/order-page/{company_slug}/")

def add_ord(request,company_slug,ref_no):
	company = Company.objects.get(slug=company_slug,user=request.user)
	ssid = request.session.session_key
	materials = Materials.objects.filter(company=company,user=request.user)
	if request.method == "POST":
		if RefNo.objects.filter(ssid=ssid,company=company).exists():
			material_id = request.POST["material_id"]
			color = request.POST["color"]
			quantity = request.POST["quantity"]
			name = Materials.objects.get(pk=material_id)
			
			ref_no=RefNo.objects.get(ssid=ssid,company=company,ref_no=ref_no,user = request.user)
			Order.objects.create(
				user = request.user,
				ref_no=ref_no,
				material=name,
				color=color,
				quantity=quantity,
				company=company
			)
			return render(request,"add_ord.html",{"company":company,"ref_no":ref_no,"materials":materials})

def view_order(request,company_slug,ref_no):
	company = Company.objects.get(slug=company_slug,user=request.user)
	ref_no = RefNo.objects.get(ref_no=ref_no,company=company,user=request.user)
	i = ref_no.ref_no
	order = Order.objects.filter(company=company,ref_no=ref_no,user=request.user)

	return render(request,"view_order.html",{"company":company,"order":order,"i":i})


def claim_dc(request,company_slug):
	company = Company.objects.get(slug=company_slug,user=request.user)
	ssid = request.session.session_key
	#ref_no = RefNo.objects.filter(company=company)
	number = DcMod.objects.filter(user=request.user)
	a = []
	for i in number:
		a.append(i.dc_no)
	print(a)
	if len(a) == 0:
		n = 1
	else:
		n = max(a)
		n += 1
	# print(max(a))
	# n = max(a)
	# no =DcMod.objects.aggregate(Max('dc_no'))
	# n= no["dc_no__max"]
	
	r = []
	print(r)
	print(n)
	q = []
	if request.method == "POST":
		r_id=request.POST.getlist('ref_id[]')
		print(r_id)
		for i in r_id:
			print("hiiiiii")
			ref = RefNo.objects.get(pk=i)
			if ref.is_claimed == False:
				ref.is_claimed = True
				ref.save()
				print(ref.is_claimed)
				r.append(ref.id)
				q.append(ref.ref_no)
				DcMod.objects.create(
					user = request.user,
					dc_no = n,
					ssid = ssid,
					ref_no = ref,
					company = company
					)
			else:
				return redirect(f"/order-page/{company_slug}/")

		print(r)	
		dc_no=n
		dc_m=DcMod.objects.filter(ssid=ssid,dc_no=n,user = request.user)
		order = Order.objects.filter(company=company,ref_no__in = r,user = request.user)
		print(order)
		return render(request,"dc_page.html",{"company":company,"dc_m":dc_m,"order":order,"dc_no":dc_no,"r":r,"q":q})

def view_dc(request,company_slug):
	company = Company.objects.get(slug=company_slug,user = request.user)
	dc_mod = DcMod.objects.filter(company = company,user=request.user).values('dc_no').distinct().order_by('-dc_no')

	return render(request,"view_dc.html",{"dc_mod":dc_mod,"company":company})

def view_items(request,company_slug,dc_no):
	company = Company.objects.get(slug=company_slug,user = request.user)
	dc_m = DcMod.objects.filter(dc_no = dc_no,company = company,user=request.user)
	r =[]
	q = []
	for i in dc_m:
		r.append(i.ref_no.id)
		q.append(i.ref_no.ref_no)
	print(r)
	print(q)
	order = Order.objects.filter(company=company,ref_no__in = r,user = request.user)
	print(order)
	return render(request,"view_items.html",{"company":company,"dc_mod":dc_m,"dc_no":dc_no,"order":order,"r":r,"q":q})

def claim_bill(request,company_slug):
	company = Company.objects.get(slug=company_slug,user = request.user)
	ssid = request.session.session_key
	number = Bill.objects.filter(user=request.user)
	a = []
	for i in number:
		a.append(i.bill_no)
	print(a)
	#print(max(a))
	if len(a) == 0:
		n = 1
	else:
		n = max(a)
		n += 1
	#n = max(a)
	# no =Bill.objects.aggregate(Max('bill_no'))
	# n= no["bill_no__max"]
	#n += 1
	r = []
	q = []
	c = []
	print(r)
	print(n)
	total = 0
	if request.method == "POST":
		dc_no=request.POST.getlist('dc_no[]')
		print("hiiii")
		print(dc_no)
		for i in dc_no:
			print("hiiiiii")
			nu = int(i)
			extra = Extra.objects.create(
				user = request.user,
				bill_no=n,
				dc_no = nu,
				company = company
				)
			dc_mod = DcMod.objects.filter(dc_no=nu,company = company,user=request.user)
			print(dc_mod)
			for i in dc_mod:
				print(i.is_claimed)
				if i.is_claimed == True:
					return redirect(f"/view_dc/{company_slug}")
				r.append(i.ref_no.id)
				q.append(i.ref_no.ref_no)
				i.is_claimed = True
				i.save()
		order = Order.objects.filter(company=company,ref_no__in = r,user=request.user)
		for i in order:
			if i.quantity < i.material.sample_quantity:
				cost = i.material.sample_rate
				c.append(cost)
				total +=cost
			else:
				cost = i.quantity * i.material.rate
				c.append(cost)
				print(i.quantity)
				print(i.material.rate)
				print(cost)
				total += cost
		print(r)
		print(cost)
		bill_no = n
		gst = (2.5/100) * total
		amount = total + 2*gst
		amount = "{:.2f}".format(amount)
		total = "{:.2f}".format(total)
		gst = "{:.2f}".format(gst)
		bill = Bill.objects.create(
				user = request.user,
				ssid = ssid,
				company = company,
				bill_no = n,
				total = total,
				gst = gst,
				amount = amount
				)
		print(bill)
		return render(request,"bill_page.html",{"company":company,"order":order,"gst":gst,"total":total,"amount":amount,"bill":bill,"bill_no":bill_no,"r":r,"q":q})

def signout(request):
	logout(request)
	return redirect("/")

class GenerateQuotation(View):
	def get(self, request, *args, **kwargs):
		company = Company.objects.get(slug = kwargs['company_slug'],user=request.user)
		print(company)
		materials = Materials.objects.filter(company = company,user = request.user)
		print(materials)
		template = get_template('quotation.html')
		context = {
			"company": company,
			"materials": materials
		}
		html = template.render(context)
		pdf = render_to_pdf('quotation.html', context)
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			filename = "quotation_%s.pdf" %("12341231")
			content = "inline; filename='%s'" %(filename)
			download = request.GET.get("download")
			if download:
				content = "attachment; filename='%s'" %(filename)
			response['Content-Disposition'] = content
			return response
		return HttpResponse("Not found")


def ledger(request):
	company = Company.objects.filter(user = request.user)
	return render(request,"ledger.html",{"company":company})

def ledgerr(request,company_slug):
	company = Company.objects.get(slug=company_slug,user = request.user)
	print(company)
	bill = Bill.objects.filter(company = company,user = request.user)
	
	return render(request,"view_ledger.html",{"company":company,"bill":bill})

def view_bill(request,company_slug,bill_no):
	company = Company.objects.get(slug=company_slug,user = request.user)
	bill = Bill.objects.get(bill_no=bill_no,user = request.user)
	extra = Extra.objects.filter(company=company,bill_no=bill_no,user=request.user)
	r = []
	q = []
	c = []
	total = 0
	for i in extra:
		print(i.dc_no)
		dc_mod = DcMod.objects.filter(dc_no=i.dc_no,company = company,user=request.user)
		for i in dc_mod:
				r.append(i.ref_no.id)
				q.append(i.ref_no.ref_no)
	print(r)
	print(q)
	order = Order.objects.filter(company=company,ref_no__in = r,user=request.user)
	for i in order:
		if i.quantity < i.material.sample_quantity:
			cost = i.material.sample_rate
			c.append(cost)
			total +=cost
		else:
			cost = i.quantity * i.material.rate
			c.append(cost)
			total += cost
	print(r)
	print(c)
	bill_no = bill_no
	gst = (2.5/100) * total
	amount = total + 2*gst
	amount = "{:.2f}".format(amount)
	total = "{:.2f}".format(total)
	gst = "{:.2f}".format(gst)
	return render(request,"bill_page.html",{"company":company,"order":order,"gst":gst,"total":total,"amount":amount,"bill":bill,"bill_no":bill_no,"r":r,"q":q,"c":c})


class GenerateDc(View):
	def get(self, request, *args, **kwargs):
		company = Company.objects.get(slug = kwargs['company_slug'],user=request.user)
		print(company)
		dc_m = DcMod.objects.filter(company = company,dc_no = kwargs['dc_no'],user=request.user)
		print(dc_m)
		r =[]
		q = []
		for i in dc_m:
			r.append(i.ref_no.id)
			q.append(i.ref_no.ref_no)
	
	
		order = Order.objects.filter(company=company,ref_no__in = r,user = request.user)
		template = get_template('dc.html')
		context = {
			"company": company,
			"dc_mod": dc_m,
			"dc_no": kwargs['dc_no'],
			"order": order,
			"q":q
		}
		html = template.render(context)
		pdf = render_to_pdf('dc.html', context)
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			filename = "dc_%s.pdf" %("12341231")
			content = "inline; filename='%s'" %(filename)
			download = request.GET.get("download")
			if download:
				content = "attachment; filename='%s'" %(filename)
			response['Content-Disposition'] = content
			return response
		return HttpResponse("Not found")



class GenerateBill(View):
	def get(self, request, *args, **kwargs):
		company = Company.objects.get(slug = kwargs['company_slug'],user=request.user)
		bill = Bill.objects.get(bill_no= kwargs['bill_no'],user=request.user)
		extra = []
		print(extra)
		extra = Extra.objects.filter(company=company,bill_no=kwargs['bill_no'],user=request.user).values('dc_no').distinct()
		print(extra)
		r = []
		q = []
		total = 0
		for i in extra:
			print(i['dc_no'])
			dc_mod = DcMod.objects.filter(dc_no=i['dc_no'],company = company,user=request.user)
			for i in dc_mod:
				r.append(i.ref_no.id)
				q.append(i.ref_no.ref_no)
		order = Order.objects.filter(company=company,ref_no__in = r,user=request.user)
		for i in order:
			if i.quantity < i.material.sample_quantity:
				cost = i.material.sample_rate
				total +=cost
			else:
				cost = i.quantity * i.material.rate
				total += cost
		print(r)
		bill_no = kwargs['bill_no']
		gst = (2.5/100) * total
		amount = total + 2*gst
		amount = "{:.2f}".format(amount)
		total = "{:.2f}".format(total)
		gst = "{:.2f}".format(gst)
		template = get_template('bill.html')
		context = {
			"company": company,
			"order": order,
			"gst":gst,
			"total":total,
			"amount":amount,
			"bill":bill,
			"bill_no":kwargs['bill_no'],
			"q":q
		}
		html = template.render(context)
		pdf = render_to_pdf('bill.html', context)
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			filename = "dc_%s.pdf" %("12341231")
			content = "inline; filename='%s'" %(filename)
			download = request.GET.get("download")
			if download:
				content = "attachment; filename='%s'" %(filename)
			response['Content-Disposition'] = content
			return response
		return HttpResponse("Not found")

@register.filter
def multiply(value, arg):
    a = value * arg
    print("hiiiii")
    g = "{:.2f}".format(a)
    print(g)
    return "{:.2f}".format(a)

