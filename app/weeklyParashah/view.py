from sqladmin import ModelView
from weeklyParashah.models import ParashaModel
from markupsafe import Markup
from redis import asyncio as aioredis
from core.config import settings
from wtforms import FileField, TextAreaField
from wtforms.validators import Optional, DataRequired,InputRequired
import json
from sqlalchemy.orm import Session
from core.database import get_db
from fastapi import Depends

redis = aioredis.from_url(settings.REDIS_URL)

CACHE_KEY = "latest_parasha_landing_page"

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
            "label": "عنوان پاراشا",
            "validators": [DataRequired()]
        },
        "description": {
            "validators": [DataRequired()],
            "label":"توضیحات پاراشا",
            "render_kw": {
                "rows": 15,
                "cols": 110,
                "dir": "rtl",
                "style": "text-align:right; direction:rtl;"
            }
        },
        "image": {
            "label": "تصویر پاراشا",
            "validators": [InputRequired()]
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

    async def on_model_change(self, data, model, is_created, request):
        image = data.get("image")

        if is_created and (not image):
            raise ValueError("تصویر پروفایل الزامی است")

        await super().on_model_change(data, model, is_created, request)

    async def after_model_change(self, data, model, is_created, request,
                                 db: Session = Depends(get_db)):
        latest_parasha = (
            db.query(ParashaModel)
            .order_by(ParashaModel.creation_date.desc())
            .first()
        )

        await redis.set(
            CACHE_KEY,
            json.dumps(latest_parasha),
            ex=3600
        )

    async def after_model_delete(self, model, request):
        await redis.delete(CACHE_KEY)