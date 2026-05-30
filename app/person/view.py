from sqladmin import ModelView
from person.models import PersonModel

class PersonAdmin(ModelView, model=PersonModel):
    name = "افراد"
    name_plural = "کاربران"
    icon = "fa-solid fa-user text-danger"

    column_list = ["name", "family_name", "is_admin","is_rabbie", "creation_date"]
    column_searchable_list = ["name", "family_name"]

    form_columns = ["name", "family_name", "is_admin","is_rabbie"]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

