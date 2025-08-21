# coding=utf-8
# django libs
from django.urls import path, include

# 3rd party libs
from rest_framework.routers import DefaultRouter

# custom import
from . import views

# Namespace for URLs in this users app
app_name = 'app_invoices'
router = DefaultRouter()
# router.register('', views.ViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('<str:invoice_id>/', views.CreateInvoice.as_view(), name='create_invoice'),
    path('', views.InvoiceListView.as_view(), name='home'),
    path('invoice_details/<str:invoice_id>/', views.InvoiceDetailsView.as_view(), name='invoice_details'),
]

# when user go to path /app_name/ it will show api root page (endpoints list)
urlpatterns += router.urls
