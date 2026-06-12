from django.shortcuts import render, redirect
from .forms import (
    CustomerForm,
    InsuranceApplicationForm,
    RiskAssessmentForm,
    UnderwritingDecisionForm,
    UnderwritingTaskForm,
)
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


def dashboard(request):
    return render(request, "dashboard.html", get_dashboard_context())


def customer_list(request):
    keyword = request.GET.get("keyword", "")
    customers = search_customers(keyword)

    return render(request, "customer_list.html", {
        "customers": customers,
        "keyword": keyword,
    })


def customer_add(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm()

    return render(request, "customer_form.html", {
        "title": "新增客户",
        "form": form,
    })


def customer_edit(request, customer_id):
    customer = get_customer_by_id(customer_id)

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm(instance=customer)

    return render(request, "customer_form.html", {
        "title": "编辑客户",
        "form": form,
    })


def customer_delete(request, customer_id):
    delete_customer(customer_id)
    return redirect("customer_list")


def application_list(request):
    keyword = request.GET.get("keyword", "")
    applications = search_applications(keyword)

    return render(request, "application_list.html", {
        "applications": applications,
        "keyword": keyword,
    })


def application_add(request):
    form = InsuranceApplicationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("application_list")

    return render(request, "application_form.html", {
        "title": "新增投保申请",
        "form": form,
    })


def application_edit(request, application_id):
    application = get_application_by_id(application_id)
    form = InsuranceApplicationForm(request.POST or None, instance=application)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("application_list")

    return render(request, "application_form.html", {
        "title": "编辑投保申请",
        "form": form,
    })


def application_delete(request, application_id):
    delete_application(application_id)
    return redirect("application_list")


def risk_assessment_list(request):
    assessments = get_risk_assessment_list()

    return render(request, "risk_assessment_list.html", {
        "assessments": assessments,
    })


def risk_assessment_edit(request, application_id):
    application = get_application_for_assessment(application_id)
    assessment = get_assessment_by_application(application)
    form = RiskAssessmentForm(request.POST or None, instance=assessment)

    if request.method == "POST" and form.is_valid():
        save_assessment(application, form)
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


def underwriting_task_add(request):
    initial = build_task_initial_from_application(request.GET.get("application"))
    form = UnderwritingTaskForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        save_underwriting_task(form)
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
        operator = request.user.username if request.user.is_authenticated else ""
        submit_underwriting_decision(task, decision_form, operator=operator)
        return redirect("underwriting_task_detail", task_id=task.id)

    return render(request, "underwriting_task_detail.html", {
        "task": task,
        "audit_logs": audit_logs,
        "can_generate_policy": can_generate_policy(task),
        "decision_form": decision_form,
    })


def underwriting_task_edit(request, task_id):
    task = get_underwriting_task_by_id(task_id)
    form = UnderwritingTaskForm(request.POST or None, instance=task)

    if request.method == "POST" and form.is_valid():
        save_underwriting_task(form)
        return redirect("underwriting_task_list")

    return render(request, "underwriting_task_form.html", {
        "title": "编辑核保任务",
        "form": form,
    })


def underwriting_task_delete(request, task_id):
    delete_underwriting_task(task_id)
    return redirect("underwriting_task_list")


def audit_log_list(request):
    audit_logs = get_audit_log_list()

    return render(request, "audit_log_list.html", {
        "audit_logs": audit_logs,
    })


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
    form = PolicyForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("policy_list")

    return render(request, "policy_form.html", {
        "title": "新增保单",
        "form": form,
    })


def policy_edit(request, policy_id):
    policy = get_policy_by_id(policy_id)
    form = PolicyForm(request.POST or None, instance=policy)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("policy_list")

    return render(request, "policy_form.html", {
        "title": "编辑保单",
        "form": form,
    })


def policy_delete(request, policy_id):
    delete_policy(policy_id)
    return redirect("policy_list")


def system_db_check(request):
    return render(request, "system_db_check.html", get_database_check_status())
