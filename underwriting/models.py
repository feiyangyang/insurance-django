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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="客户")
    policy_no = models.CharField("保单号", max_length=50, unique=True)
    product_name = models.CharField("产品名称", max_length=100)
    premium = models.DecimalField("保费", max_digits=10, decimal_places=2)
    insured_amount = models.DecimalField("保额", max_digits=12, decimal_places=2)

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