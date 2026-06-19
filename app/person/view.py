from sqladmin import ModelView
from person.models import PersonModel
from markupsafe import Markup
from wtforms import FileField
from wtforms.validators import Optional


class PersonView(ModelView, model=PersonModel):
    name = "افراد"
    name_plural = "اشخاص"
    icon = "fa-solid fa-user text-danger"

    column_list = ["name", "family_name", "is_admin", "is_rabbie", "image", "creation_date"]
    column_searchable_list = ["name", "family_name"]

    form_columns = ["name", "family_name", "is_admin", "is_rabbie", "image"]
    form_overrides = {
        "image": FileField,  # ImageField رو به FileField تبدیل کن
    }

    column_formatters = {
        "image": lambda m, a: Markup(
            f'<img src="/static/person_images/{m.image.path.split("/")[-1]}" '
            f'width="70" style="max-height:70px; object-fit:cover; border-radius:5px;">'
        ) if m.image and m.image.path else "بدون تصویر"
    }
    column_details_formatters = {
        "image": lambda m, a: Markup(
            f'<img src="/static/parasha_images/{m.image.path.split("/")[-1]}" '
            f'width="300" style="max-height:300px; object-fit:cover; border-radius:10px; border:1px solid #ddd;" />'
        ) if m.image and m.image.path else "-"
    }

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True