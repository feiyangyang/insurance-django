from django import forms
from .models import Customer, InsuranceApplication, Policy, RiskAssessment, UnderwritingTask


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "customer_type",
            "name",
            "gender",
            "age",
            "phone",
            "id_number",
            "company_name",
            "unified_social_credit_code",
            "contact_person",
            "contact_phone",
            "registered_address",
        ]
        widgets = {
            "customer_type": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "个人姓名或企业简称"}),
            "gender": forms.Select(
                choices=[("", "请选择"), ("男", "男"), ("女", "女")],
                attrs={"class": "form-select"}
            ),
            "age": forms.NumberInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "id_number": forms.TextInput(attrs={"class": "form-control"}),
            "company_name": forms.TextInput(attrs={"class": "form-control"}),
            "unified_social_credit_code": forms.TextInput(attrs={"class": "form-control"}),
            "contact_person": forms.TextInput(attrs={"class": "form-control"}),
            "contact_phone": forms.TextInput(attrs={"class": "form-control"}),
            "registered_address": forms.TextInput(attrs={"class": "form-control"}),
        }


class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = [
            "customer",
            "application",
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
            "application": forms.Select(attrs={"class": "form-select"}),
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


class InsuranceApplicationForm(forms.ModelForm):
    class Meta:
        model = InsuranceApplication
        fields = [
            "application_no",
            "customer",
            "insurance_type",
            "subject_name",
            "subject_address",
            "insured_amount",
            "estimated_premium",
            "status",
            "remark",
        ]
        widgets = {
            "application_no": forms.TextInput(attrs={"class": "form-control"}),
            "customer": forms.Select(attrs={"class": "form-select"}),
            "insurance_type": forms.Select(attrs={"class": "form-select"}),
            "subject_name": forms.TextInput(attrs={"class": "form-control"}),
            "subject_address": forms.TextInput(attrs={"class": "form-control"}),
            "insured_amount": forms.NumberInput(attrs={"class": "form-control"}),
            "estimated_premium": forms.NumberInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "remark": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class RiskAssessmentForm(forms.ModelForm):
    class Meta:
        model = RiskAssessment
        fields = [
            "risk_level",
            "risk_score",
            "risk_factors",
            "conclusion",
        ]
        widgets = {
            "risk_level": forms.Select(attrs={"class": "form-select"}),
            "risk_score": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 100}),
            "risk_factors": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "conclusion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean_risk_score(self):
        risk_score = self.cleaned_data["risk_score"]
        if risk_score > 100:
            raise forms.ValidationError("风险评分不能超过 100")
        return risk_score


class UnderwritingTaskForm(forms.ModelForm):
    class Meta:
        model = UnderwritingTask
        fields = [
            "task_no",
            "application",
            "policy",
            "health_notice",
            "risk_level",
            "status",
            "assigned_to",
            "remark",
        ]
        widgets = {
            "task_no": forms.TextInput(attrs={"class": "form-control"}),
            "application": forms.Select(attrs={"class": "form-select"}),
            "policy": forms.Select(attrs={"class": "form-select"}),
            "health_notice": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "risk_level": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "assigned_to": forms.TextInput(attrs={"class": "form-control"}),
            "remark": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        application = cleaned_data.get("application")
        policy = cleaned_data.get("policy")

        if not application and not policy:
            raise forms.ValidationError("投保申请和保单至少选择一项")

        return cleaned_data


class UnderwritingDecisionForm(forms.Form):
    status = forms.ChoiceField(
        label="核保结论",
        choices=UnderwritingTask.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    risk_level = forms.ChoiceField(
        label="风险等级",
        choices=UnderwritingTask.RISK_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    remark = forms.CharField(
        label="核保意见",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
    )
