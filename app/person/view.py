from sqladmin import ModelView
from person.models import PersonModel

class PersonAdmin(ModelView, model=PersonModel):
    name = "افراد"
    name_plural = "کاربران"
    icon = "fa-solid fa-user text-danger"

    column_list = ["email", "phone", "is_admin", "creation_date"]
    column_searchable_list = ["email", "phone"]

    form_columns = ["email", "phone", "is_admin"]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

