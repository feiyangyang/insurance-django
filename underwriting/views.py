from urllib.parse import urlencode

from django import forms as django_forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import (
    CompanyForm,
    CustomerForm,
    DepartmentForm,
    FormFieldConfigurationForm,
    FormTemplateForm,
    InsuranceApplicationForm,
    LoginForm,
    PasswordResetForm,
    RiskAssessmentForm,
    SystemRoleForm,
    SystemUserForm,
    UnderwritingDecisionForm,
    UnderwritingTaskForm,
)
from .models import (
    Company,
    Department,
    FormFieldConfiguration,
    FormTemplate,
    OperationLog,
    PermissionPoint,
    SystemRole,
    UserProfile,
)
from .security import log_operation, permission_required, user_has_permission
from .services.customer_service import (
    get_customer_list,
    get_customer_by_id,
    delete_customer,
    search_customers,
)

from .forms import PolicyForm
from .services.policy_service import (
    can_generate_policy,
    generate_policy_from_task,
    search_policies,
    get_policy_by_id,
    delete_policy,
)
from .services.dashboard_service import get_dashboard_context
from .services.application_service import (
    delete_application,
    get_application_by_id,
    search_applications,
)
from .services.audit_service import get_audit_log_list, get_audit_logs_for_task
from .services.risk_service import (
    get_application_for_assessment,
    get_assessment_by_application,
    get_risk_assessment_list,
    save_assessment,
)
from .services.underwriting_service import (
    build_task_initial_from_application,
    delete_underwriting_task,
    get_underwriting_task_by_id,
    save_underwriting_task,
    search_underwriting_tasks,
    submit_underwriting_decision,
)
from .services.system_check_service import get_database_check_status


def login_view(request):
    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":
        username = request.POST.get("username", "")
        if form.is_valid():
            login(request, form.get_user())
            log_operation(request, "登录", "登录成功", description=f"{username} 登录系统")
            return redirect(request.GET.get("next") or "dashboard")
        OperationLog.objects.create(
            username=username,
            module="登录",
            action="登录失败",
            description=f"{username} 登录失败",
            path=request.path,
            result="failed",
        )

    return render(request, "login.html", {"form": form})


def logout_view(request):
    log_operation(request, "登录", "退出登录", description="退出系统")
    logout(request)
    return redirect("login")


def _apply_config_to_form(form, field_configs):
    for config in field_configs:
        if config.field_key not in form.fields:
            continue

        field = form.fields[config.field_key]
        field.label = config.field_label
        field.required = config.is_required
        field.help_text = config.help_text

        if config.default_value and not form.is_bound and not form.initial.get(config.field_key):
            form.initial[config.field_key] = config.default_value

        if config.field_key == "customer":
            continue

        widget_attrs = dict(field.widget.attrs)
        css_class = "form-check-input" if config.control_type == "checkbox" else "form-select" if config.control_type == "select" else "form-control"
        widget_attrs["class"] = css_class

        if config.help_text and config.control_type not in {"checkbox", "select"}:
            widget_attrs["placeholder"] = config.help_text

        if config.control_type == "textarea":
            widget_attrs["rows"] = widget_attrs.get("rows", 3)
            field.widget = django_forms.Textarea(attrs=widget_attrs)
        elif config.control_type == "number":
            field.widget = django_forms.NumberInput(attrs=widget_attrs)
        elif config.control_type == "date":
            field.widget = django_forms.DateInput(attrs=widget_attrs)
        elif config.control_type == "checkbox":
            field.widget = django_forms.CheckboxInput(attrs=widget_attrs)


def _get_form_template(form_type):
    return (
        FormTemplate.objects.filter(form_type=form_type, is_active=True)
        .prefetch_related("fields")
        .order_by("id")
        .first()
    )


def _build_configured_form_fields(form, form_type):
    template = _get_form_template(form_type)
    configured_fields = []

    if template:
        field_configs = list(template.fields.filter(is_enabled=True))
        _apply_config_to_form(form, field_configs)

        for config in field_configs:
            if config.field_key in form.fields:
                configured_fields.append({
                    "config": config,
                    "field": form[config.field_key],
                    "key": config.field_key,
                    "is_customer_picker": config.field_key == "customer",
                    "wide": config.control_type == "textarea",
                })
    else:
        for field_name in form.fields:
            configured_fields.append({
                "config": None,
                "field": form[field_name],
                "key": field_name,
                "is_customer_picker": field_name == "customer",
                "wide": field_name == "remark",
            })

    return template, configured_fields


def _build_customer_picker_context(form):
    selected_customer = None
    selected_customer_id = form.data.get("customer") if form.is_bound else form.initial.get("customer")

    if selected_customer_id:
        selected_customer_id = getattr(selected_customer_id, "id", selected_customer_id)
        try:
            selected_customer = get_customer_by_id(selected_customer_id)
        except Exception:
            selected_customer = None

    return {
        "customers": get_customer_list(),
        "selected_customer": selected_customer,
    }


def dashboard(request):
    return render(request, "dashboard.html", get_dashboard_context())


def customer_list(request):
    keyword = request.GET.get("keyword", "")
    customers = search_customers(keyword)

    return render(request, "customer_list.html", {
        "customers": customers,
        "keyword": keyword,
    })


@permission_required("customer.create")
def customer_add(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            log_operation(request, "客户管理", "新增客户", customer, customer.customer_no)
            return redirect("customer_list")
    else:
        form = CustomerForm()

    return render(request, "customer_form.html", {
        "title": "新增客户",
        "form": form,
    })


@permission_required("customer.edit")
def customer_edit(request, customer_id):
    customer = get_customer_by_id(customer_id)

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save()
            log_operation(request, "客户管理", "编辑客户", customer, customer.customer_no)
            return redirect("customer_list")
    else:
        form = CustomerForm(instance=customer)

    return render(request, "customer_form.html", {
        "title": "编辑客户",
        "form": form,
    })


@permission_required("customer.delete")
def customer_delete(request, customer_id):
    customer = get_customer_by_id(customer_id)
    delete_customer(customer_id)
    log_operation(request, "客户管理", "删除客户", customer, customer.customer_no)
    return redirect("customer_list")


def application_list(request):
    keyword = request.GET.get("keyword", "")
    applications = search_applications(keyword)

    return render(request, "application_list.html", {
        "applications": applications,
        "keyword": keyword,
    })


@permission_required("application.create")
def application_add(request):
    form = InsuranceApplicationForm(request.POST or None)
    application_template, configured_fields = _build_configured_form_fields(form, "application")

    if request.method == "POST" and form.is_valid():
        application = form.save()
        log_operation(request, "投保申请", "新增投保申请", application, application.application_no)
        return redirect("application_list")

    return render(request, "application_form.html", {
        "title": "新增投保申请",
        "form": form,
        "application_template": application_template,
        "configured_fields": configured_fields,
        **_build_customer_picker_context(form),
    })


@permission_required("application.edit")
def application_edit(request, application_id):
    application = get_application_by_id(application_id)
    form = InsuranceApplicationForm(request.POST or None, instance=application)
    application_template, configured_fields = _build_configured_form_fields(form, "application")

    if request.method == "POST" and form.is_valid():
        application = form.save()
        log_operation(request, "投保申请", "编辑投保申请", application, application.application_no)
        return redirect("application_list")

    return render(request, "application_form.html", {
        "title": "编辑投保申请",
        "form": form,
        "application_template": application_template,
        "configured_fields": configured_fields,
        **_build_customer_picker_context(form),
    })


@permission_required("application.delete")
def application_delete(request, application_id):
    application = get_application_by_id(application_id)
    delete_application(application_id)
    log_operation(request, "投保申请", "删除投保申请", application, application.application_no)
    return redirect("application_list")


def risk_assessment_list(request):
    assessments = get_risk_assessment_list()

    return render(request, "risk_assessment_list.html", {
        "assessments": assessments,
    })


@permission_required("risk.edit")
def risk_assessment_edit(request, application_id):
    application = get_application_for_assessment(application_id)
    assessment = get_assessment_by_application(application)
    form = RiskAssessmentForm(request.POST or None, instance=assessment)

    if request.method == "POST" and form.is_valid():
        save_assessment(application, form)
        log_operation(request, "风险评估", "保存风险评估", application, application.application_no)
        return redirect("application_list")

    return render(request, "risk_assessment_form.html", {
        "application": application,
        "assessment": assessment,
        "form": form,
    })


def underwriting_task_list(request):
    keyword = request.GET.get("keyword", "")
    tasks = search_underwriting_tasks(keyword)

    return render(request, "underwriting_task_list.html", {
        "tasks": tasks,
        "keyword": keyword,
    })


@permission_required("underwriting.create")
def underwriting_task_add(request):
    initial = build_task_initial_from_application(request.GET.get("application"))
    form = UnderwritingTaskForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        task = save_underwriting_task(form)
        log_operation(request, "核保任务", "新增核保任务", task, task.task_no)
        return redirect("underwriting_task_list")

    return render(request, "underwriting_task_form.html", {
        "title": "新增核保任务",
        "form": form,
    })


def underwriting_task_detail(request, task_id):
    task = get_underwriting_task_by_id(task_id)
    audit_logs = get_audit_logs_for_task(task)
    decision_form = UnderwritingDecisionForm(
        request.POST or None,
        initial={
            "status": task.status,
            "risk_level": task.risk_level,
            "remark": task.remark,
        },
    )

    if request.method == "POST" and decision_form.is_valid():
        if not user_has_permission(request.user, "underwriting.decision"):
            raise PermissionDenied
        operator = request.user.username if request.user.is_authenticated else ""
        submit_underwriting_decision(task, decision_form, operator=operator)
        log_operation(request, "核保任务", "提交核保结论", task, task.task_no)
        return redirect("underwriting_task_detail", task_id=task.id)

    return render(request, "underwriting_task_detail.html", {
        "task": task,
        "audit_logs": audit_logs,
        "can_generate_policy": can_generate_policy(task),
        "decision_form": decision_form,
    })


@permission_required("underwriting.edit")
def underwriting_task_edit(request, task_id):
    task = get_underwriting_task_by_id(task_id)
    form = UnderwritingTaskForm(request.POST or None, instance=task)

    if request.method == "POST" and form.is_valid():
        task = save_underwriting_task(form)
        log_operation(request, "核保任务", "编辑核保任务", task, task.task_no)
        return redirect("underwriting_task_list")

    return render(request, "underwriting_task_form.html", {
        "title": "编辑核保任务",
        "form": form,
    })


@permission_required("underwriting.delete")
def underwriting_task_delete(request, task_id):
    task = get_underwriting_task_by_id(task_id)
    delete_underwriting_task(task_id)
    log_operation(request, "核保任务", "删除核保任务", task, task.task_no)
    return redirect("underwriting_task_list")


def audit_log_list(request):
    audit_logs = get_audit_log_list()

    return render(request, "audit_log_list.html", {
        "audit_logs": audit_logs,
    })


@permission_required("policy.edit")
def generate_policy(request, task_id):
    task = get_underwriting_task_by_id(task_id)
    operator = request.user.username if request.user.is_authenticated else ""
    generate_policy_from_task(task, operator=operator)
    return redirect("underwriting_task_detail", task_id=task.id)


def policy_list(request):
    keyword = request.GET.get("keyword", "")
    policies = search_policies(keyword)

    return render(request, "policy_list.html", {
        "policies": policies,
        "keyword": keyword,
    })


def policy_add(request):
    messages.warning(request, "保单只能由核保流程生成，不能手工新增。")
    return redirect("policy_list")


@permission_required("policy.edit")
def policy_edit(request, policy_id):
    policy = get_policy_by_id(policy_id)
    form = PolicyForm(request.POST or None, instance=policy)
    policy_task = policy.underwritingtask_set.order_by("-updated_at").first()
    policy_risk_assessment = None
    if policy.application:
        try:
            policy_risk_assessment = policy.application.risk_assessment
        except Exception:
            policy_risk_assessment = None

    if request.method == "POST" and form.is_valid():
        policy = form.save()
        log_operation(request, "保单管理", "编辑保单", policy, policy.policy_no)
        return redirect("policy_list")

    return render(request, "policy_form.html", {
        "title": "编辑保单",
        "form": form,
        "policy": policy,
        "policy_task": policy_task,
        "policy_risk_assessment": policy_risk_assessment,
    })


@permission_required("policy.delete")
def policy_delete(request, policy_id):
    policy = get_policy_by_id(policy_id)
    delete_policy(policy_id)
    log_operation(request, "保单管理", "删除保单", policy, policy.policy_no)
    return redirect("policy_list")


@permission_required("system.db_check")
def system_db_check(request):
    return render(request, "system_db_check.html", get_database_check_status())


@permission_required("system.company")
def company_management(request):
    company_id = request.GET.get("company")
    selected_company = Company.objects.filter(id=company_id).first() if company_id else None
    form = CompanyForm(instance=selected_company)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete" and selected_company:
            log_operation(request, "公司管理", "删除公司", selected_company, selected_company.name)
            selected_company.delete()
            return redirect("company_management")

        form = CompanyForm(request.POST, instance=selected_company)
        if form.is_valid():
            company = form.save()
            log_operation(request, "公司管理", "保存公司", company, company.name)
            return redirect(f"{reverse('company_management')}?company={company.id}")

    return render(request, "company_management.html", {
        "companies": Company.objects.all(),
        "selected_company": selected_company,
        "form": form,
    })


@permission_required("system.department")
def department_management(request):
    department_id = request.GET.get("department")
    selected_department = Department.objects.filter(id=department_id).select_related("company").first() if department_id else None
    form = DepartmentForm(instance=selected_department)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete" and selected_department:
            log_operation(request, "部门管理", "删除部门", selected_department, selected_department.name)
            selected_department.delete()
            return redirect("department_management")

        form = DepartmentForm(request.POST, instance=selected_department)
        if form.is_valid():
            department = form.save()
            log_operation(request, "部门管理", "保存部门", department, department.name)
            return redirect(f"{reverse('department_management')}?department={department.id}")

    return render(request, "department_management.html", {
        "departments": Department.objects.select_related("company"),
        "selected_department": selected_department,
        "form": form,
    })


@permission_required("system.user")
def user_management(request):
    user_id = request.GET.get("user")
    selected_user = User.objects.filter(id=user_id).first() if user_id else None
    form = SystemUserForm(user_instance=selected_user)
    password_form = PasswordResetForm()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete" and selected_user:
            log_operation(request, "用户管理", "删除用户", selected_user, selected_user.username)
            selected_user.delete()
            return redirect("user_management")
        if action == "reset_password" and selected_user:
            password_form = PasswordResetForm(request.POST)
            if password_form.is_valid():
                selected_user.set_password(password_form.cleaned_data["password"])
                selected_user.save(update_fields=["password"])
                log_operation(request, "用户管理", "重置密码", selected_user, selected_user.username)
                messages.success(request, "密码已重置")
                return redirect(f"{reverse('user_management')}?user={selected_user.id}")

        form = SystemUserForm(request.POST, user_instance=selected_user)
        if form.is_valid():
            user = selected_user or User()
            user.username = form.cleaned_data["username"]
            user.first_name = form.cleaned_data["full_name"]
            user.is_active = form.cleaned_data["is_active"]
            if not selected_user or form.cleaned_data.get("password"):
                user.set_password(form.cleaned_data["password"])
            user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.company = form.cleaned_data["company"]
            profile.department = form.cleaned_data["department"]
            profile.remark = form.cleaned_data["remark"]
            profile.save()
            profile.roles.set(form.cleaned_data["roles"])
            log_operation(request, "用户管理", "保存用户", user, user.username)
            return redirect(f"{reverse('user_management')}?user={user.id}")

    users = list(User.objects.all().order_by("username"))
    for item in users:
        UserProfile.objects.get_or_create(user=item)

    return render(request, "user_management.html", {
        "users": User.objects.select_related("profile__company", "profile__department").all().order_by("username"),
        "selected_user": selected_user,
        "form": form,
        "password_form": password_form,
    })


@permission_required("system.role")
def role_permission_management(request):
    role_id = request.GET.get("role")
    selected_role = SystemRole.objects.filter(id=role_id).prefetch_related("permissions").first() if role_id else None
    form = SystemRoleForm(instance=selected_role)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete" and selected_role:
            log_operation(request, "角色权限", "删除角色", selected_role, selected_role.name)
            selected_role.delete()
            return redirect("role_permission_management")

        form = SystemRoleForm(request.POST, instance=selected_role)
        if form.is_valid():
            role = form.save()
            log_operation(request, "角色权限", "保存角色权限", role, role.name)
            return redirect(f"{reverse('role_permission_management')}?role={role.id}")

    permissions_by_module = {}
    for permission in PermissionPoint.objects.all():
        permissions_by_module.setdefault(permission.module, []).append(permission)

    return render(request, "role_permission_management.html", {
        "roles": SystemRole.objects.prefetch_related("permissions"),
        "selected_role": selected_role,
        "form": form,
        "permissions_by_module": permissions_by_module,
    })


@permission_required("system.operation_log")
def operation_log_list(request):
    keyword = request.GET.get("keyword", "")
    module = request.GET.get("module", "")
    logs = OperationLog.objects.select_related("user")

    if keyword:
        logs = logs.filter(
            Q(username__icontains=keyword)
            | Q(description__icontains=keyword)
            | Q(target_type__icontains=keyword)
            | Q(target_id__icontains=keyword)
        )
    if module:
        logs = logs.filter(module=module)

    return render(request, "operation_log_list.html", {
        "logs": logs[:300],
        "keyword": keyword,
        "module": module,
        "modules": OperationLog.objects.values_list("module", flat=True).distinct(),
    })


def _form_config_redirect(template_id=None, field_id=None, customer_type="personal", form_type=None):
    params = {}
    if template_id:
        params["template"] = template_id
    if field_id:
        params["field"] = field_id
    if customer_type:
        params["customer_type"] = customer_type
    if form_type:
        params["form_type"] = form_type

    url = reverse("form_configuration")
    if params:
        url = f"{url}?{urlencode(params)}"
    return redirect(url)


@permission_required("system.form_config")
def form_configuration(request):
    selected_form_type = request.GET.get("form_type", "customer")
    if selected_form_type not in {"customer", "application"}:
        selected_form_type = "customer"

    templates = FormTemplate.objects.filter(form_type=selected_form_type).prefetch_related("fields")
    template_id = request.GET.get("template")
    field_id = request.GET.get("field")
    is_create_mode = request.GET.get("mode") == "new"
    customer_type = request.GET.get("customer_type", "personal")
    selected_template = None if is_create_mode else templates.filter(id=template_id).first() if template_id else templates.first()
    selected_field = None

    if selected_template and field_id:
        selected_field = selected_template.fields.filter(id=field_id).first()

    template_form = (
        FormTemplateForm(instance=selected_template)
        if selected_template
        else FormTemplateForm(initial={"form_type": selected_form_type})
    )
    field_form = FormFieldConfigurationForm(instance=selected_field)

    if request.method == "POST":
        action = request.POST.get("action")
        customer_type = request.POST.get("customer_type", customer_type)

        if action == "create_template":
            template_form = FormTemplateForm(request.POST)
            if template_form.is_valid():
                template = template_form.save()
                return _form_config_redirect(template.id, customer_type=customer_type, form_type=template.form_type)
        elif action == "update_template" and selected_template:
            template_form = FormTemplateForm(request.POST, instance=selected_template)
            if template_form.is_valid():
                template = template_form.save()
                return _form_config_redirect(template.id, customer_type=customer_type, form_type=template.form_type)
        elif action == "delete_template" and selected_template:
            deleted_form_type = selected_template.form_type
            selected_template.delete()
            return _form_config_redirect(customer_type=customer_type, form_type=deleted_form_type)
        elif action == "create_field" and selected_template:
            field_form = FormFieldConfigurationForm(request.POST)
            if field_form.is_valid():
                field = field_form.save(commit=False)
                field.template = selected_template
                field.save()
                return _form_config_redirect(selected_template.id, field.id, customer_type, selected_template.form_type)
        elif action == "update_field" and selected_template and selected_field:
            field_form = FormFieldConfigurationForm(request.POST, instance=selected_field)
            if field_form.is_valid():
                field = field_form.save()
                return _form_config_redirect(selected_template.id, field.id, customer_type, selected_template.form_type)
        elif action == "delete_field" and selected_template and selected_field:
            selected_field.delete()
            return _form_config_redirect(selected_template.id, customer_type=customer_type, form_type=selected_template.form_type)

    configured_fields = []
    all_fields = []
    if selected_template:
        all_fields = selected_template.fields.all()
        fields = all_fields.filter(is_enabled=True)
        if customer_type in {"personal", "company"}:
            fields = fields.filter(customer_type__in=["all", customer_type])
        configured_fields = fields

    return render(request, "form_configuration.html", {
        "templates": templates,
        "selected_form_type": selected_form_type,
        "selected_template": selected_template,
        "selected_field": selected_field,
        "selected_customer_type": customer_type,
        "template_form": template_form,
        "field_form": field_form,
        "all_fields": all_fields,
        "configured_fields": configured_fields,
    })


def knowledge_agent(request):
    return render(request, "knowledge_agent.html")


def help_center(request):
    return render(request, "help_center.html")
