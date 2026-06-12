from django.db import models


class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ("personal", "个人客户"),
        ("company", "企业客户"),
    ]

    customer_type = models.CharField(
        "客户类型",
        max_length=20,
        choices=CUSTOMER_TYPE_CHOICES,
        default="personal",
    )
    name = models.CharField("客户名称", max_length=100)
    gender = models.CharField("性别", max_length=10, blank=True)
    age = models.IntegerField("年龄", null=True, blank=True)
    phone = models.CharField("手机号", max_length=20, blank=True)
    id_number = models.CharField("身份证号", max_length=30, blank=True)
    company_name = models.CharField("企业名称", max_length=100, blank=True)
    unified_social_credit_code = models.CharField(
        "统一社会信用代码",
        max_length=50,
        blank=True,
    )
    contact_person = models.CharField("联系人", max_length=50, blank=True)
    contact_phone = models.CharField("联系电话", max_length=20, blank=True)
    registered_address = models.CharField("注册地址", max_length=200, blank=True)

    def __str__(self):
        if self.customer_type == "company" and self.company_name:
            return self.company_name
        return self.name


class Policy(models.Model):
    POLICY_STATUS_CHOICES = [
        ("draft", "草稿"),
        ("submitted", "已提交"),
        ("underwriting", "核保中"),
        ("approved", "已承保"),
        ("rejected", "拒保"),
        ("cancelled", "已取消"),
    ]

    PAY_MODE_CHOICES = [
        ("single", "趸交"),
        ("yearly", "年交"),
        ("monthly", "月交"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="客户")
    application = models.OneToOneField(
        "InsuranceApplication",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="policy",
        verbose_name="投保申请",
    )

    policy_no = models.CharField("保单号", max_length=50, unique=True)
    proposal_no = models.CharField("投保单号", max_length=50, blank=True)

    product_name = models.CharField("产品名称", max_length=100)
    product_type = models.CharField("产品类型", max_length=50, blank=True)

    applicant_name = models.CharField("投保人姓名", max_length=50, blank=True)
    insured_name = models.CharField("被保人姓名", max_length=50, blank=True)
    relation = models.CharField("投被保人关系", max_length=30, blank=True)

    premium = models.DecimalField("年缴保费", max_digits=10, decimal_places=2)
    insured_amount = models.DecimalField("基本保额", max_digits=12, decimal_places=2)

    pay_mode = models.CharField("缴费方式", max_length=20, choices=PAY_MODE_CHOICES, default="yearly")
    pay_period = models.CharField("缴费期间", max_length=30, blank=True)
    coverage_period = models.CharField("保障期间", max_length=30, blank=True)

    effective_date = models.DateField("生效日期", null=True, blank=True)
    expiry_date = models.DateField("终止日期", null=True, blank=True)

    sales_channel = models.CharField("销售渠道", max_length=50, blank=True)
    agent_name = models.CharField("业务员/渠道人员", max_length=50, blank=True)

    status = models.CharField("保单状态", max_length=30, choices=POLICY_STATUS_CHOICES, default="submitted")
    remark = models.TextField("备注", blank=True)

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    def __str__(self):
        return self.policy_no


class InsuranceApplication(models.Model):
    INSURANCE_TYPE_CHOICES = [
        ("auto", "车险"),
        ("property", "财产险"),
        ("liability", "责任险"),
        ("engineering", "工程险"),
        ("cargo", "货运险"),
        ("other", "其他"),
    ]

    STATUS_CHOICES = [
        ("draft", "草稿"),
        ("submitted", "已提交"),
        ("underwriting", "核保中"),
        ("approved", "通过"),
        ("rejected", "拒保"),
        ("need_material", "补充资料"),
        ("cancelled", "已取消"),
    ]

    application_no = models.CharField("投保申请号", max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="客户")
    insurance_type = models.CharField(
        "险种类型",
        max_length=30,
        choices=INSURANCE_TYPE_CHOICES,
        default="property",
    )
    subject_name = models.CharField("保险标的", max_length=100)
    subject_address = models.CharField("标的地址", max_length=200, blank=True)
    insured_amount = models.DecimalField("保险金额", max_digits=12, decimal_places=2)
    estimated_premium = models.DecimalField("预估保费", max_digits=10, decimal_places=2)
    status = models.CharField("申请状态", max_length=30, choices=STATUS_CHOICES, default="submitted")
    remark = models.TextField("备注", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    def __str__(self):
        return self.application_no


class RiskAssessment(models.Model):
    RISK_LEVEL_CHOICES = [
        ("low", "低风险"),
        ("medium", "中风险"),
        ("high", "高风险"),
    ]

    application = models.OneToOneField(
        InsuranceApplication,
        on_delete=models.CASCADE,
        related_name="risk_assessment",
        verbose_name="投保申请",
    )
    risk_level = models.CharField(
        "风险等级",
        max_length=20,
        choices=RISK_LEVEL_CHOICES,
        default="medium",
    )
    risk_score = models.PositiveIntegerField("风险评分", default=50)
    risk_factors = models.TextField("风险因素", blank=True)
    conclusion = models.TextField("评估结论", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    def __str__(self):
        return f"{self.application.application_no} - {self.get_risk_level_display()}"


class UnderwritingTask(models.Model):
    STATUS_CHOICES = [
        ("pending", "待核保"),
        ("reviewing", "审核中"),
        ("approved", "通过"),
        ("extra_fee", "加费"),
        ("excluded", "除外"),
        ("postponed", "延期"),
        ("rejected", "拒保"),
        ("need_material", "补充资料"),
    ]

    RISK_CHOICES = [
        ("low", "低风险"),
        ("medium", "中风险"),
        ("high", "高风险"),
    ]

    application = models.ForeignKey(
        InsuranceApplication,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="投保申请",
    )
    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="保单",
    )
    task_no = models.CharField("任务编号", max_length=50, unique=True)
    health_notice = models.TextField("健康告知", blank=True)
    risk_level = models.CharField("风险等级", max_length=20, choices=RISK_CHOICES, default="medium")
    status = models.CharField("核保状态", max_length=30, choices=STATUS_CHOICES, default="pending")
    assigned_to = models.CharField("核保人员", max_length=50, blank=True)
    remark = models.TextField("备注", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    def __str__(self):
        return self.task_no


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("decision", "提交结论"),
        ("create_policy", "生成保单"),
        ("update", "更新"),
    ]

    task = models.ForeignKey(UnderwritingTask, on_delete=models.CASCADE, verbose_name="核保任务")
    action = models.CharField("操作类型", max_length=30, choices=ACTION_CHOICES, default="decision")
    operator = models.CharField("操作人", max_length=50, blank=True)
    from_status = models.CharField("原状态", max_length=30, blank=True)
    to_status = models.CharField("新状态", max_length=30, blank=True)
    decision = models.CharField("核保结论", max_length=50)
    comment = models.TextField("审核意见", blank=True)
    created_at = models.DateTimeField("审核时间", auto_now_add=True)

    def __str__(self):
        return f"{self.task.task_no} - {self.decision}"
