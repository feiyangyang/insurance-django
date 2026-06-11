from django.db import models


class Customer(models.Model):
    name = models.CharField("客户姓名", max_length=50)
    gender = models.CharField("性别", max_length=10, blank=True)
    age = models.IntegerField("年龄")
    phone = models.CharField("手机号", max_length=20, blank=True)
    id_number = models.CharField("身份证号", max_length=30, blank=True)

    def __str__(self):
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

    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, verbose_name="保单")
    task_no = models.CharField("任务编号", max_length=50, unique=True)
    health_notice = models.TextField("健康告知", blank=True)
    risk_level = models.CharField("风险等级", max_length=20, choices=RISK_CHOICES, default="medium")
    status = models.CharField("核保状态", max_length=30, choices=STATUS_CHOICES, default="pending")
    remark = models.TextField("备注", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    def __str__(self):
        return self.task_no


class AuditLog(models.Model):
    task = models.ForeignKey(UnderwritingTask, on_delete=models.CASCADE, verbose_name="核保任务")
    decision = models.CharField("核保结论", max_length=50)
    comment = models.TextField("审核意见", blank=True)
    created_at = models.DateTimeField("审核时间", auto_now_add=True)

    def __str__(self):
        return f"{self.task.task_no} - {self.decision}"