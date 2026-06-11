from django import forms
from .models import Customer, Policy


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "gender", "age", "phone", "id_number"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(
                choices=[("男", "男"), ("女", "女")],
                attrs={"class": "form-select"}
            ),
            "age": forms.NumberInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "id_number": forms.TextInput(attrs={"class": "form-control"}),
        }


class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = [
            "customer",
            "policy_no",
            "proposal_no",
            "product_name",
            "product_type",
            "applicant_name",
            "insured_name",
            "relation",
            "premium",
            "insured_amount",
            "pay_mode",
            "pay_period",
            "coverage_period",
            "effective_date",
            "expiry_date",
            "sales_channel",
            "agent_name",
            "status",
            "remark",
        ]

        widgets = {
            "customer": forms.Select(attrs={"class": "form-select"}),
            "policy_no": forms.TextInput(attrs={"class": "form-control"}),
            "proposal_no": forms.TextInput(attrs={"class": "form-control"}),
            "product_name": forms.TextInput(attrs={"class": "form-control"}),
            "product_type": forms.TextInput(attrs={"class": "form-control"}),
            "applicant_name": forms.TextInput(attrs={"class": "form-control"}),
            "insured_name": forms.TextInput(attrs={"class": "form-control"}),
            "relation": forms.TextInput(attrs={"class": "form-control"}),
            "premium": forms.NumberInput(attrs={"class": "form-control"}),
            "insured_amount": forms.NumberInput(attrs={"class": "form-control"}),
            "pay_mode": forms.Select(attrs={"class": "form-select"}),
            "pay_period": forms.TextInput(attrs={"class": "form-control"}),
            "coverage_period": forms.TextInput(attrs={"class": "form-control"}),
            "effective_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "expiry_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "sales_channel": forms.TextInput(attrs={"class": "form-control"}),
            "agent_name": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "remark": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }