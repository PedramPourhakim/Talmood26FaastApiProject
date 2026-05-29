from sqladmin import ModelView
from weeklyParashah.models import ParashaModel
from wtforms import Form, StringField, TextAreaField, FileField
from wtforms.validators import DataRequired
from utils.FileManager import delete_old_image, save_file
from markupsafe import Markup


class ParashaForm(Form):
    title = StringField(
        "عنوان",
        validators=[DataRequired()]
    )

    description = TextAreaField(
        "توضیحات",
        validators=[DataRequired()]
    )

    image_file = FileField("تصویر")


class ParashaView(ModelView, model=ParashaModel):

    name = 'پاراشا'
    name_plural = 'پاراشاهای هفتگی'
    icon = "fa-solid fa-star-of-david text-danger"

    form = ParashaForm

    column_list = [
        "title",
        "image_path",
        "description",
        "creation_date",
    ]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    column_formatters = {
        "image_path": lambda model, attribute: Markup(
            f'<img src="{model.image_path}" width="100" height="70" '
            f'style="object-fit:cover;border-radius:8px;border:1px solid #ddd;" />'
        ) if model.image_path else "-"
    }

    column_details_formatters = {
        "image_path": lambda model, attribute: Markup(
            f'<img src="{model.image_path}" width="300" '
            f'style="object-fit:cover;border-radius:10px;border:1px solid #ddd;" />'
        ) if model.image_path else "-"
    }

    async def on_model_change(self, data, model, is_created, request):

        form = await request.form()

        image_file = form.get("image_file")

        if is_created and not (
            image_file and image_file.filename
        ):
            raise ValueError("آپلود تصویر الزامی است")

        if image_file and image_file.filename:

            if not is_created and model.image_path:
                delete_old_image(model.image_path)

            saved_path = save_file(image_file)

            model.image_path = saved_path

    async def on_model_delete(self, model, request):

        if model.image_path:
            delete_old_image(model.image_path)