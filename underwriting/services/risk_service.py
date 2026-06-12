from django.shortcuts import get_object_or_404

from underwriting.models import InsuranceApplication, RiskAssessment


def get_risk_assessment_list():
    return (
        RiskAssessment.objects.select_related("application", "application__customer")
        .all()
        .order_by("-updated_at", "-id")
    )


def get_application_for_assessment(application_id):
    return get_object_or_404(
        InsuranceApplication.objects.select_related("customer"),
        id=application_id,
    )


def get_assessment_by_application(application):
    try:
        return application.risk_assessment
    except RiskAssessment.DoesNotExist:
        return None


def save_assessment(application, form):
    assessment = form.save(commit=False)
    assessment.application = application
    assessment.save()
    return assessment
