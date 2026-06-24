from sqladmin import ModelView
from qa.models import QAModel
from person.models import PersonModel
from wtforms.validators import DataRequired
from wtforms import SelectField

class QAView(ModelView, model=QAModel):
    name = 'پرسش و پاسخ'
    name_plural = 'پرسش و پاسخ از ربانیم'
    icon = 'fa-solid fa-question-circle text-danger'

    column_list = ["is_answered",
                    "rabbie", "talmid"]
    column_searchable_list = ["talmid", "rabbie"]

    form_columns = [
        "talmid",
        "question",
        "answer",
        "is_answered"
    ]

    async def scaffold_form(self, rules=None):
        form_class = await super().scaffold_form()

        session = self.session_maker()
        rabbies = (
            session.query(PersonModel)
            .filter(PersonModel.is_rabbie == True)
            .all()
        )

        form_class.rabbie_select = SelectField(
            "ربی",
            choices=[
                (str(p.id), f"{p.name} {p.family_name}")
                for p in rabbies
            ],
            validators=[DataRequired()],
            render_kw={
                "class": "form-select"
            }
        )

        return form_class

    async def on_model_change(self, data, model, is_created, request):
        model.rabbie_id = data["rabbie_select"]

        await super().on_model_change(
            data,
            model,
            is_created,
            request
        )
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
