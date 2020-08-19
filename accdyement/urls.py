"""accdyement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from dyeing.views import *
urlpatterns = [
    path('',home),
    path('admin/', admin.site.urls),
    path('signup/',owner_signup),
    path('signin/',owner_signin),
    path('signout/',signout),
    path('dashboard/',dashboard),
    path('create-company/',create_company),
    path('company-page/',company_page),
    path('rate-page/<int:company_id>/',rate_page),
    path('create-material/<int:company_id>/',create_material),
    path('order-page/<slug:company_slug>/',order_page),
    path('add-ref/<slug:company_slug>/',add_ref),
    path('add-ord/<slug:company_slug>/<int:ref_no>/',add_ord),
    path('remove/<int:material_id>/',remove_material),
    path('edit_material/<int:material_id>/',edit_material),
    path('claim-dc/<slug:company_slug>/',claim_dc),
    path('view_order/<slug:company_slug>/<int:ref_no>/',view_order),
    path('view_dc/<slug:company_slug>/',view_dc),
    path('view_items/<slug:company_slug>/<int:dc_no>/',view_items),
    path('claim-bill/<slug:company_slug>/',claim_bill),
    path('quotation/<slug:company_slug>/',GenerateQuotation.as_view()),
    #path('quotation/<slug:company_slug>/',quotation),
    path('ledger/',ledger),
    path('ledger/<slug:company_slug>/',ledgerr),
    path('view_bill/<slug:company_slug>/<int:bill_no>/',view_bill),
    path('dc/<slug:company_slug>/<int:dc_no>/',GenerateDc.as_view()),
    path('bill/<slug:company_slug>/<int:bill_no>/',GenerateBill.as_view()),
    
]
