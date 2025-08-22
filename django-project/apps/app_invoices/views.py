# coding=utf-8
#=====[ Built-in / Standard Library ]=====
import re
import tempfile
#=====[ Django Core Imports ]=====
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles import finders
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, UpdateView,CreateView, FormView, TemplateView, DeleteView, View
#=====[ Third-party Packages ]=====
from django_ratelimit.decorators import ratelimit
from weasyprint import HTML
from .signals import generate_invoice_number
from .models import InvoiceModel
from .forms import InvoiceModelForm
from apps.app_quotations.models import QuotationInformationModel
from apps.app_employee.models import EmployeesModel



# Class Base Views
# Home
@method_decorator(ratelimit(key='header:X-Forwarded-For', rate=settings.RATE_LIMIT, block=True), name='dispatch')
class InvoiceListView(LoginRequiredMixin, ListView):
    login_url = 'users:login'
    model = InvoiceModel
    template_name = 'app_invoices/home.html'
    context_object_name = 'all_invoices'

    #Search / Filter Function
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                invoice_id__icontains = search
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['title'] = 'ລາຍການໃບເກັບເງິນທັງຫມົດ'
        return context

# Create Invoice 
@method_decorator(ratelimit(key='header:X-Forwarded-For', rate=settings.RATE_LIMIT, block=True), name='dispatch')
# class CreateInvoice(LoginRequiredMixin, View):
#     template_name = 'app_invoices/create_invoice.html'

#     def get(self, request, *args, **kwargs):
#         quotation_id = kwargs.get('invoice_id')
#         quotation = get_object_or_404(QuotationInformationModel, quotation_id=quotation_id)
#         additional_expense = quotation.additional_payments.first()  # ดึงตัวแรก

#         form = InvoiceModelForm(initial={
#             'quotation': quotation,
#             'issue_date': quotation.start_date,
#             'due_date': quotation.end_date,
#         })

#         context = {
#             'form': form,
#             'quotation': quotation,
#             'additional_expense': additional_expense,
#             'title': 'ອອກໃບເກັບເງິນ'
#         }
#         return render(request, self.template_name, context)

#     def post(self, request, *args, **kwargs):
#         quotation_id = kwargs.get('invoice_id')
#         quotation = get_object_or_404(QuotationInformationModel, quotation_id=quotation_id)
#         additional_expense = quotation.additional_payments.first()

#         form = InvoiceModelForm(request.POST, request.FILES)
#         if form.is_valid():
#             invoice = form.save(commit=False)
#             invoice.quotation = quotation

#             # แปลง request.user เป็น EmployeesModel
#             employee = EmployeesModel.objects.get(user=request.user)
#             invoice.created_by = employee

#             invoice.save()
#             return redirect('app_invoices:home')

#         context = {
#             'form': form,
#             'quotation': quotation,
#             'additional_expense': additional_expense,
#             'title': 'ອອກໃບເກັບເງິນ'
#         }
#         return render(request, self.template_name, context)

@method_decorator(
    ratelimit(key='header:X-Forwarded-For', rate=settings.RATE_LIMIT, block=True), 
    name='dispatch'
)
class CreateInvoice(LoginRequiredMixin, View):
    login_url = 'users:login'
    template_name = 'app_invoices/create_invoice.html'

    def get(self, request, *args, **kwargs):
        quotation_id = kwargs.get('invoice_id')
        quotation = get_object_or_404(QuotationInformationModel, quotation_id=quotation_id)
        additional_expense = quotation.additional_payments.first()

        form = InvoiceModelForm(
            initial={
                'quotation': quotation,
                'issue_date': quotation.start_date,
                'due_date': quotation.end_date
            }
        )
        context = {
            'form': form,
            'quotation': quotation,
            'additional_expense': additional_expense,
            'title': 'ອອກໃບເກັບເງິນ'
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        quotation_id = kwargs.get('invoice_id')
        quotation = get_object_or_404(QuotationInformationModel, quotation_id=quotation_id)
        additional_expense = quotation.additional_payments.first()

        form = InvoiceModelForm(request.POST, request.FILES)

        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.quotation = quotation
            employee = EmployeesModel.objects.get(user=request.user)
            invoice.created_by = employee

            # if invoice of quotation existing already
            existing_invoice = InvoiceModel.objects.filter(quotation=quotation).first()

            if existing_invoice and not request.POST.get('confirm_update'):
                # Notification to User
                messages.warning(
                    request, 
                    "ມີໃບເກັບເງິນຂອງໃບສະເຫນີລາຄານີ້ແລ້ວ, ຕ້ອງການອັບເດດຫລືບໍ່?"
                )
                context = {
                    'form': form,
                    'quotation': quotation,
                    'additional_expense': additional_expense,
                    'title': 'ຢືນຢັນການອັບເດດໃບເກັບເງິນ',
                    'confirm_update': True,
                    'existing_invoice': existing_invoice
                }
                return render(request, self.template_name, context)

            if existing_invoice and request.POST.get('confirm_update'):
                # If confirmed_update invoice
                # Update invoice
                existing_invoice.issue_date = invoice.issue_date
                existing_invoice.due_date = invoice.due_date
                existing_invoice.created_by = invoice.created_by
                
                if invoice.invoice_signatured:
                    existing_invoice.invoice_signatured = invoice.invoice_signatured

                if invoice.customer_payment:
                    existing_invoice.customer_payment = invoice.customer_payment
                    
                existing_invoice.save()
            else:
                # create new invoice
                invoice.save()

            return redirect('app_invoices:home')

        # if form is not valid will be redirect to render
        context = {
            'form': form,
            'quotation': quotation,
            'additional_expense': additional_expense,
            'title': 'ອອກໃບເກັບເງິນ'
        }
        return render(request, self.template_name, context)


# One Invoice Details View
class InvoiceDetailsView(LoginRequiredMixin, DetailView):
    login_url = 'users:login'
    model = InvoiceModel
    template_name = 'app_invoices/invoice_details.html'
    get_context_data = 'one_invoice'
    slug_field = 'invoice_id'
    slug_url_kwarg = 'invoice_id'
