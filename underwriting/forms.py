from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import (
    Company,
    Customer,
    Department,
    FormFieldConfiguration,
    FormTemplate,
    InsuranceApplication,
    PermissionPoint,
    Policy,
    RiskAssessment,
    SystemRole,
    UnderwritingTask,
    UserProfile,
)


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="登录账号",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "请输入账号"}),
    )
    password = forms.CharField(
        label="登录密码",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "请输入密码"}),
    )


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "code", "is_active", "remark"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "remark": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["company", "name", "code", "is_active", "remark"]
        widgets = {
            "company": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "remark": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class SystemRoleForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        label="授权权限",
        queryset=PermissionPoint.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = SystemRole
        fields = ["name", "code", "permissions", "is_active", "remark"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "remark": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["permissions"].queryset = PermissionPoint.objects.all()


class SystemUserForm(forms.Form):
    username = forms.CharField(label="登录账号", max_length=150, widget=forms.TextInput(attrs={"class": "form-control"}))
    full_name = forms.CharField(label="用户姓名", max_length=150, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(label="登录密码", required=False, widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password_confirm = forms.CharField(label="确认密码", required=False, widget=forms.PasswordInput(attrs={"class": "form-control"}))
    company = forms.ModelChoiceField(label="所属公司", queryset=Company.objects.none(), required=False, widget=forms.Select(attrs={"class": "form-select"}))
    department = forms.ModelChoiceField(label="所属部门", queryset=Department.objects.none(), required=False, widget=forms.Select(attrs={"class": "form-select"}))
    roles = forms.ModelMultipleChoiceField(label="角色", queryset=SystemRole.objects.none(), required=False, widget=forms.CheckboxSelectMultiple)
    is_active = forms.BooleanField(label="启用", required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
    remark = forms.CharField(label="备注", required=False, widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}))

    def __init__(self, *args, user_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_instance = user_instance
        self.fields["company"].queryset = Company.objects.filter(is_active=True)
        self.fields["department"].queryset = Department.objects.filter(is_active=True).select_related("company")
        self.fields["roles"].queryset = SystemRole.objects.filter(is_active=True)
        if user_instance:
            profile, _ = UserProfile.objects.get_or_create(user=user_instance)
            self.fields["password"].required = False
            self.fields["password_confirm"].required = False
            self.initial.update({
                "username": user_instance.username,
                "full_name": user_instance.get_full_name(),
                "company": profile.company_id,
                "department": profile.department_id,
                "roles": profile.roles.all(),
                "is_active": user_instance.is_active,
                "remark": profile.remark,
            })
        else:
            self.fields["password"].required = True
            self.fields["password_confirm"].required = True
            self.initial["is_active"] = True

    def clean_username(self):
        username = self.cleaned_data["username"]
        queryset = User.objects.filter(username=username)
        if self.user_instance:
            queryset = queryset.exclude(id=self.user_instance.id)
        if queryset.exists():
            raise forms.ValidationError("登录账号已存在")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password or password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("两次输入的密码不一致")
        return cleaned_data


class PasswordResetForm(forms.Form):
    password = forms.CharField(label="新密码", widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password_confirm = forms.CharField(label="确认密码", widget=forms.PasswordInput(attrs={"class": "form-control"}))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("password_confirm"):
            raise forms.ValidationError("两次输入的密码不一致")
        return cleaned_data


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


class FormTemplateForm(forms.ModelForm):
    class Meta:
        model = FormTemplate
        fields = [
            "name",
            "code",
            "form_type",
            "customer_type",
            "description",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "例如：客户信息采集模板"}),
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "例如：customer-intake"}),
            "form_type": forms.Select(attrs={"class": "form-select"}),
            "customer_type": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class FormFieldConfigurationForm(forms.ModelForm):
    class Meta:
        model = FormFieldConfiguration
        fields = [
            "sort_order",
            "field_label",
            "field_key",
            "control_type",
            "customer_type",
            "is_required",
            "default_value",
            "option_values",
            "help_text",
            "is_enabled",
        ]
        widgets = {
            "sort_order": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "field_label": forms.TextInput(attrs={"class": "form-control", "placeholder": "例如：统一社会信用代码"}),
            "field_key": forms.TextInput(attrs={"class": "form-control", "placeholder": "例如：credit_code"}),
            "control_type": forms.Select(attrs={"class": "form-select"}),
            "customer_type": forms.Select(attrs={"class": "form-select"}),
            "is_required": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "default_value": forms.TextInput(attrs={"class": "form-control"}),
            "option_values": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "下拉选择时每行一个选项"}),
            "help_text": forms.TextInput(attrs={"class": "form-control", "placeholder": "输入框提示或业务说明"}),
            "is_enabled": forms.CheckboxInput(attrs={"class": "form-check-input"}),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ["customer", "application", "policy_no", "proposal_no"]:
            if field_name in self.fields:
                self.fields[field_name].disabled = True


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
            "customer": forms.HiddenInput(),
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
