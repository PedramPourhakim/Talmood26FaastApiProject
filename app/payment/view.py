from sqladmin import ModelView
from payment.models import PaymentModel

class PaymentView(ModelView,model=PaymentModel):
    name = "مدیریت تراکنش های بانکی"
    name_plural = ""
    icon = "fa-solid fa-money-check-dollar text-danger"

    column_list = ["person", "amount", "description","status","ref_id","paid_at","payment_account"]
    column_searchable_list = ["payment_account"]

    form_columns = ["person", "amount", "description", "status","payment_account"]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True