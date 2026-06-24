from sqladmin import ModelView
from paymentType.models import PaymentTypeModel

class PaymentTypeView(ModelView,model=PaymentTypeModel):
    name = "نوع پرداخت"
    name_plural = "نوع های پرداختی"
    icon = "fa-solid fa-credit-card text-danger"

    column_list = ["id","title"]
    column_searchable_list = ["title"]

    form_columns = ["title"]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

