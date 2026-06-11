from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "gender", "age", "phone", "id_number"]
        labels = {
            "name": "客户姓名",
            "gender": "性别",
            "age": "年龄",
            "phone": "手机号",
            "id_number": "身份证号",
        }
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