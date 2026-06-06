from sqladmin import ModelView
from users.models import UserModel

class UserView(ModelView,model=UserModel):
    name = "حساب کاربری"
    name_plural = "حساب های کاربری"
    icon = "fa-solid fa-user text-danger"

    column_list = ["email", "phone","person","creation_date"]
    column_searchable_list = ["email", "phone"]

    form_columns = ["email", "phone", "person"]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

