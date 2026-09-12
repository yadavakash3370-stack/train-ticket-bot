from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def btn(text, callback_data=None, style=None, url=None):
    kwargs = {"text": text}

    if callback_data:
        kwargs["callback_data"] = callback_data

    if style:
        kwargs["style"] = style

    if url:
        kwargs["url"] = url

    return InlineKeyboardButton(**kwargs)


def main_menu(user_id=None, admin_id=None):
    buttons = [
        [
            btn("🚆 Search Train", "search_train", "primary"),
            btn("👤 My Profile", "profile", "primary"),
        ],
        [
            btn("🧳 My Journey", "my_journey", "primary"),
            btn("📅 My Bookings", "my_bookings", "primary"),
        ],
        [
            btn("🔔 Alerts", "alerts", "primary"),
            btn("💾 Saved Journeys", "saved_journeys"),
        ],
    ]

    # Sirf admin ko Admin Panel
    if user_id is not None and admin_id is not None:
        if str(user_id) == str(admin_id):
            buttons.append([
                btn("⚙️ Admin Panel", "admin_panel", "danger")
            ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [btn("⬅️ Back to Menu", "back_menu", "primary")]
        ]
    )


def admin_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                btn("📊 Stats", "admin_stats", "primary"),
                btn("👥 Users", "admin_users", "primary"),
            ],
            [
                btn("📢 Broadcast", "admin_broadcast", "success"),
                btn("💬 Message User", "admin_message", "primary"),
            ],
            [
                btn("🚆 Journeys", "admin_journeys", "primary"),
                btn("🔔 Monitoring", "admin_monitoring", "primary"),
            ],
            [
                btn("📋 Logs", "admin_logs"),
                btn("⚙️ System Status", "admin_status", "primary"),
            ],
            [
                btn("⬅️ Back", "back_menu")
            ],
        ]
    )


def train_list_keyboard(trains):
    buttons = []

    for train in trains:
        buttons.append([
            btn(
                f"🚆 {train['number']} • {train['name']}",
                f"train_{train['number']}",
                "primary"
            )
        ])

    buttons.append([
        btn("⬅️ Back", "back_menu")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def class_keyboard(train_number):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                btn("1A", f"class_{train_number}_1A", "primary"),
                btn("2A", f"class_{train_number}_2A", "primary"),
            ],
            [
                btn("3A", f"class_{train_number}_3A", "primary"),
                btn("SL", f"class_{train_number}_SL"),
            ],
            [
                btn("⬅️ Back", "search_train")
            ],
        ]
    )


def payment_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                btn("💳 Demo Payment", "demo_payment", "success")
            ],
            [
                btn("❌ Cancel", "cancel_booking", "danger")
            ],
        ]
    )


def confirm_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                btn("✅ Confirm Booking", "confirm_booking", "success"),
                btn("❌ Cancel", "cancel_booking", "danger"),
            ]
        ]
    )
