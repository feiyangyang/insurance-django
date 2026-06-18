from django.test import TestCase
from django.urls import reverse

from .models import Customer, FormFieldConfiguration, FormTemplate


class FormConfigurationViewTests(TestCase):
    def setUp(self):
        self.client.login(username="admin", password="Admin@123456")
        self.template = FormTemplate.objects.create(
            name="测试客户模板",
            code="test-customer-template",
            customer_type="all",
            is_active=True,
        )
        FormFieldConfiguration.objects.create(
            template=self.template,
            field_key="customer_name",
            field_label="客户名称",
            control_type="text",
            customer_type="all",
            is_required=True,
            sort_order=10,
        )
        FormFieldConfiguration.objects.create(
            template=self.template,
            field_key="id_number",
            field_label="身份证号",
            control_type="text",
            customer_type="personal",
            sort_order=20,
        )
        FormFieldConfiguration.objects.create(
            template=self.template,
            field_key="company_name",
            field_label="企业名称",
            control_type="text",
            customer_type="company",
            sort_order=30,
        )

    def test_form_configuration_filters_personal_fields(self):
        response = self.client.get(
            reverse("form_configuration"),
            {"template": self.template.id, "customer_type": "personal"},
        )

        self.assertEqual(response.status_code, 200)
        labels = [field.field_label for field in response.context["configured_fields"]]
        self.assertEqual(labels, ["客户名称", "身份证号"])

    def test_form_configuration_filters_company_fields(self):
        response = self.client.get(
            reverse("form_configuration"),
            {"template": self.template.id, "customer_type": "company"},
        )

        self.assertEqual(response.status_code, 200)
        labels = [field.field_label for field in response.context["configured_fields"]]
        self.assertEqual(labels, ["客户名称", "企业名称"])

    def test_form_configuration_new_template_mode_is_blank(self):
        response = self.client.get(
            reverse("form_configuration"),
            {"mode": "new", "form_type": "application", "customer_type": "personal"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["selected_template"])
        self.assertEqual(response.context["selected_form_type"], "application")
        self.assertContains(response, "新建模板")
        self.assertContains(response, "先创建模板")

    def test_form_configuration_filters_templates_by_form_type(self):
        FormTemplate.objects.create(
            name="测试投保模板",
            code="test-application-template",
            form_type="application",
            customer_type="all",
            is_active=True,
        )

        response = self.client.get(reverse("form_configuration"), {"form_type": "application"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "测试投保模板")
        self.assertNotContains(response, "测试客户模板")

    def test_form_configuration_creates_field_without_admin(self):
        response = self.client.post(
            f"{reverse('form_configuration')}?template={self.template.id}",
            {
                "action": "create_field",
                "customer_type": "company",
                "sort_order": 40,
                "field_label": "联系人",
                "field_key": "contact_person",
                "control_type": "text",
                "default_value": "",
                "option_values": "",
                "help_text": "",
                "is_enabled": "on",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            FormFieldConfiguration.objects.filter(
                template=self.template,
                field_key="contact_person",
                customer_type="company",
            ).exists()
        )

    def test_knowledge_agent_placeholder_renders(self):
        response = self.client.get(reverse("knowledge_agent"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "企业内部知识库 Agent")

    def test_help_center_renders_business_flow(self):
        response = self.client.get(reverse("help_center"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "帮助中心")
        self.assertContains(response, "主业务流程")
        self.assertContains(response, "创建客户")
        self.assertContains(response, "提交投保申请")
        self.assertContains(response, "提交核保结论")

    def test_application_form_uses_searchable_customer_picker(self):
        Customer.objects.create(
            customer_type="personal",
            name="张三",
            phone="13800000000",
            id_number="110101199001010011",
        )
        Customer.objects.create(
            customer_type="company",
            name="示例企业",
            company_name="示例科技有限公司",
            unified_social_credit_code="91310000TEST000001",
            contact_person="李四",
            contact_phone="13900000000",
        )

        response = self.client.get(reverse("application_add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "搜索客户")
        self.assertContains(response, "张三")
        self.assertContains(response, "示例科技有限公司")
        self.assertContains(response, 'id="id_customer"', html=False)
        self.assertNotContains(response, '<select name="customer"', html=False)
