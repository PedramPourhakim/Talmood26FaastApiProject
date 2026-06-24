from sqladmin import ModelView
from paymentAccount.models import PaymentAccountModel

class PaymentAccountView(ModelView,model=PaymentAccountModel):
    name = "مشخصات حساب مربوط به پرداخت"
    name_plural = ""
    icon = "fa-solid fa-hand-holding-dollar text-danger"

    column_list = ["account_title","payment_type","person"]
    column_searchable_list = ["account_title"]

    form_columns = ["payment_type","account_title","person","sheba_number"]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

