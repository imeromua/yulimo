"""CMS: clients, media, email_logs, email_templates, content_blocks, site_settings, booking.client_id

Revision ID: a1b2c3d4e5f6
Revises: 03a9b44482dd
Create Date: 2026-03-13 06:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "03a9b44482dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- clients ---
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("email", sa.String(100), nullable=True),
        sa.Column("birthday", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source", sa.String(20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone"),
    )
    op.create_index(op.f("ix_clients_id"), "clients", ["id"], unique=False)

    # --- add client_id to bookings ---
    with op.batch_alter_table("bookings") as batch_op:
        batch_op.add_column(sa.Column("client_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_bookings_client_id", "clients", ["client_id"], ["id"])

    # --- media ---
    op.create_table(
        "media",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("section", sa.String(50), nullable=False, server_default="other"),
        sa.Column("title_uk", sa.String(255), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("1")),
        sa.Column("uploaded_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("filename"),
    )
    op.create_index(op.f("ix_media_id"), "media", ["id"], unique=False)

    # --- email_logs ---
    op.create_table(
        "email_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipient_email", sa.String(100), nullable=False),
        sa.Column("recipient_name", sa.String(100), nullable=True),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("template_type", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), nullable=True, server_default="pending"),
        sa.Column("booking_id", sa.Integer(), nullable=True),
        sa.Column("sent_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_email_logs_id"), "email_logs", ["id"], unique=False)

    # --- email_templates ---
    op.create_table(
        "email_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("body_html", sa.Text(), nullable=False),
        sa.Column("template_type", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("1")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("template_type"),
    )
    op.create_index(op.f("ix_email_templates_id"), "email_templates", ["id"], unique=False)

    # --- Seed default email templates ---
    op.bulk_insert(
        sa.table(
            "email_templates",
            sa.column("name", sa.String),
            sa.column("subject", sa.String),
            sa.column("body_html", sa.Text),
            sa.column("template_type", sa.String),
            sa.column("is_active", sa.Boolean),
        ),
        [
            {
                "name": "Підтвердження бронювання",
                "subject": "Бронювання №{{booking_id}} підтверджено — Юлімо",
                "body_html": (
                    "<h2>Вітаємо, {{guest_name}}!</h2>"
                    "<p>Ваше бронювання №{{booking_id}} підтверджено.</p>"
                    "<p>Заїзд: <strong>{{check_in}}</strong>, виїзд: <strong>{{check_out}}</strong></p>"
                    "<p>Кількість ночей: {{nights}}, сума: {{total_price}} грн</p>"
                ),
                "template_type": "booking_confirm",
                "is_active": True,
            },
            {
                "name": "Нагадування про заїзд",
                "subject": "Нагадування: ваш заїзд {{check_in}} — Юлімо",
                "body_html": (
                    "<h2>Нагадування для {{guest_name}}</h2>"
                    "<p>Нагадуємо, що ваш заїзд — <strong>{{check_in}}</strong>.</p>"
                    "<p>Чекаємо вас на базі відпочинку Юлімо!</p>"
                ),
                "template_type": "booking_reminder",
                "is_active": True,
            },
            {
                "name": "Скасування бронювання",
                "subject": "Бронювання №{{booking_id}} скасовано — Юлімо",
                "body_html": (
                    "<h2>Шановний(-а) {{guest_name}},</h2>"
                    "<p>На жаль, ваше бронювання №{{booking_id}} (заїзд {{check_in}}) було скасовано.</p>"
                    "<p>З питань звертайтеся за телефоном: +38 (073) 537-60-37</p>"
                ),
                "template_type": "booking_cancelled",
                "is_active": True,
            },
            {
                "name": "Привітання з днем народження",
                "subject": "З Днем народження від Юлімо! 🎂",
                "body_html": (
                    "<h2>Вітаємо, {{guest_name}}!</h2>"
                    "<p>Команда бази відпочинку Юлімо щиро вітає вас з Днем народження!</p>"
                    "<p>Бажаємо радості та незабутнього відпочинку!</p>"
                ),
                "template_type": "birthday",
                "is_active": True,
            },
        ],
    )

    # --- content_blocks ---
    op.create_table(
        "content_blocks",
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("label", sa.String(200), nullable=False),
        sa.Column("value", sa.Text(), nullable=False, server_default=""),
        sa.Column("block_type", sa.String(20), nullable=True, server_default="text"),
        sa.Column("section", sa.String(50), nullable=True, server_default="other"),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.PrimaryKeyConstraint("key"),
    )

    # --- Seed content blocks ---
    op.bulk_insert(
        sa.table(
            "content_blocks",
            sa.column("key", sa.String),
            sa.column("label", sa.String),
            sa.column("value", sa.Text),
            sa.column("block_type", sa.String),
            sa.column("section", sa.String),
        ),
        [
            {"key": "hero_title", "label": "Заголовок героя", "value": "Відпочинок, який хочеться повторити", "block_type": "text", "section": "hero"},
            {"key": "hero_subtitle", "label": "Підзаголовок героя", "value": "База відпочинку Юлімо у Пущі-Водиці", "block_type": "text", "section": "hero"},
            {"key": "about_title", "label": "Заголовок розділу Про нас", "value": "Про нас", "block_type": "text", "section": "about"},
            {"key": "about_text_1", "label": "Текст про нас (1)", "value": "Ласкаво просимо на базу відпочинку Юлімо — місце, де природа та комфорт поєднуються для вашого ідеального відпочинку.", "block_type": "html", "section": "about"},
            {"key": "about_text_2", "label": "Текст про нас (2)", "value": "Ми пропонуємо затишні номери, смачну кухню та безліч розваг для всієї родини.", "block_type": "html", "section": "about"},
            {"key": "restaurant_description", "label": "Опис ресторану", "value": "Наш ресторан пропонує страви української та європейської кухні з місцевих продуктів.", "block_type": "html", "section": "restaurant"},
            {"key": "footer_description", "label": "Опис у футері", "value": "База відпочинку Юлімо — ваш відпочинок у Пущі-Водиці.", "block_type": "text", "section": "footer"},
            {"key": "checkin_time", "label": "Час заїзду", "value": "14:00", "block_type": "text", "section": "services"},
            {"key": "checkout_time", "label": "Час виїзду", "value": "12:00", "block_type": "text", "section": "services"},
            {"key": "phone_1", "label": "Телефон 1", "value": "+380735376037", "block_type": "text", "section": "footer"},
            {"key": "phone_2", "label": "Телефон 2", "value": "+380985376037", "block_type": "text", "section": "footer"},
        ],
    )

    # --- site_settings ---
    op.create_table(
        "site_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.Text(), nullable=False, server_default=""),
        sa.Column("label", sa.String(200), nullable=False),
        sa.Column("group", sa.String(50), nullable=False, server_default="general"),
        sa.Column("setting_type", sa.String(20), nullable=True, server_default="text"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index(op.f("ix_site_settings_id"), "site_settings", ["id"], unique=False)

    # --- Seed site settings ---
    op.bulk_insert(
        sa.table(
            "site_settings",
            sa.column("key", sa.String),
            sa.column("value", sa.Text),
            sa.column("label", sa.String),
            sa.column("group", sa.String),
            sa.column("setting_type", sa.String),
        ),
        [
            {"key": "site_name", "value": "Юлімо", "label": "Назва сайту", "group": "general", "setting_type": "text"},
            {"key": "site_tagline", "value": "База відпочинку у Пущі-Водиці", "label": "Слоган", "group": "general", "setting_type": "text"},
            {"key": "address", "value": "Пуща-Водиця, Київ", "label": "Адреса", "group": "general", "setting_type": "text"},
            {"key": "contact_phone_1", "value": "+380735376037", "label": "Телефон 1", "group": "contacts", "setting_type": "text"},
            {"key": "contact_phone_2", "value": "+380985376037", "label": "Телефон 2", "group": "contacts", "setting_type": "text"},
            {"key": "contact_email", "value": "", "label": "Email", "group": "contacts", "setting_type": "text"},
            {"key": "instagram_url", "value": "", "label": "Instagram", "group": "social", "setting_type": "url"},
            {"key": "facebook_url", "value": "", "label": "Facebook", "group": "social", "setting_type": "url"},
            {"key": "telegram_url", "value": "", "label": "Telegram", "group": "social", "setting_type": "url"},
            {"key": "meta_title", "value": "Юлімо — База відпочинку у Пущі-Водиці", "label": "Meta Title", "group": "seo", "setting_type": "text"},
            {"key": "meta_description", "value": "Відпочинок у Пущі-Водиці — затишні котеджі, ресторан, природа.", "label": "Meta Description", "group": "seo", "setting_type": "text"},
            {"key": "meta_keywords", "value": "база відпочинку, Пуща-Водиця, котеджі, відпочинок", "label": "Meta Keywords", "group": "seo", "setting_type": "text"},
            {"key": "maintenance_mode", "value": "false", "label": "Режим обслуговування", "group": "features", "setting_type": "boolean"},
            {"key": "booking_enabled", "value": "true", "label": "Бронювання увімкнено", "group": "features", "setting_type": "boolean"},
            {"key": "season_banner_enabled", "value": "false", "label": "Сезонний банер увімкнено", "group": "features", "setting_type": "boolean"},
            {"key": "season_banner_text", "value": "", "label": "Текст сезонного банера", "group": "features", "setting_type": "text"},
            {"key": "google_analytics_id", "value": "", "label": "Google Analytics ID", "group": "seo", "setting_type": "text"},
        ],
    )


def downgrade() -> None:
    op.drop_table("site_settings")
    op.drop_table("content_blocks")
    op.drop_table("email_templates")
    op.drop_table("email_logs")
    op.drop_table("media")
    with op.batch_alter_table("bookings") as batch_op:
        batch_op.drop_constraint("fk_bookings_client_id", type_="foreignkey")
        batch_op.drop_column("client_id")
    op.drop_index(op.f("ix_clients_id"), table_name="clients")
    op.drop_table("clients")
