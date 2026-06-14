from sqladmin import ModelView
from weeklyParashah.models import ParashaModel
from markupsafe import Markup

from wtforms import FileField, TextAreaField
from wtforms.validators import Optional, DataRequired


class ParashaView(ModelView, model=ParashaModel):

    name = 'پاراشا'
    name_plural = 'پاراشاهای هفتگی'
    icon = "fa-solid fa-star-of-david text-danger"

    form_columns = ["title", "description", "image"]

    column_list = ["title", "image", "description", "creation_date"]
    column_searchable_list = ["title", "description"]

    # Override فیلدها
    form_overrides = {
        "image": FileField,
        "description": TextAreaField,   # ← این خط مهم است
    }

    form_args = {
        "title": {
            "validators": [DataRequired()]
        },
        "description": {
            "validators": [DataRequired()],
            "render_kw": {
                "rows": 15,
                "cols": 110,
                "dir": "rtl",
                "style": "text-align:right; direction:rtl;"
            }
        },
        "image": {
            "label": "تصویر پاراشا",
            "validators": [Optional()]
        }
    }

    # نمایش تصویر در لیست
    column_formatters = {
        "image": lambda m, a: Markup(
            f'<img src="/static/parasha_images/{m.image.path.split("/")[-1]}" '
            f'width="100" style="max-height:70px; object-fit:cover; border-radius:8px; border:1px solid #ddd;" />'
        ) if m.image and m.image.path else "-"
    }

    # نمایش تصویر در جزئیات
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