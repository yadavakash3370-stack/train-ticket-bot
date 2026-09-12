from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def button(text, callback_data, style=None):

    kwargs = {
        "text": text,
        "callback_data": callback_data,
    }

    if style:
        kwargs["style"] = style

    return InlineKeyboardButton(**kwargs)


def main_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button(
                    "👤 Passenger Profile",
                    "profile",
                    "primary",
                )
            ],
            [
                button(
                    "🚆 Book Ticket",
                    "book_ticket",
                    "success",
                ),
                button(
                    "🔎 Search Train",
                    "search_train",
                    "primary",
                ),
            ],
            [
                button(
                    "📋 My Journeys",
                    "my_journeys",
                ),
                button(
                    "🔔 My Alerts",
                    "alerts",
                ),
            ],
            [
                button(
                    "⚙️ Settings",
                    "settings",
                )
            ],
        ]
    )


def back_home():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button(
                    "🏠 Home",
                    "home",
                    "primary",
                )
            ]
        ]
    )


def profile_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button(
                    "➕ Add Passenger",
                    "add_passenger",
                    "success",
                )
            ],
            [
                button(
                    "📋 View Profile",
                    "view_profile",
                )
            ],
            [
                button(
                    "✏️ Edit Profile",
                    "edit_profile",
                )
            ],
            [
                button(
                    "🗑 Delete Profile",
                    "delete_profile",
                    "danger",
                )
            ],
            [
                button(
                    "◀️ Back",
                    "home",
                )
            ],
        ]
    )


def gender_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button("👨 Male", "gender_male", "primary"),
                button("👩 Female", "gender_female", "primary"),
            ],
            [
                button("◀️ Cancel", "profile")
            ],
        ]
    )


def berth_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button("Lower", "berth_lower"),
                button("Middle", "berth_middle"),
            ],
            [
                button("Upper", "berth_upper"),
                button("Side Lower", "berth_sl"),
            ],
            [
                button("Side Upper", "berth_su"),
            ],
            [
                button("◀️ Cancel", "profile"),
            ],
        ]
    )


def journey_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button(
                    "📍 From Station",
                    "journey_from",
                    "primary",
                )
            ],
            [
                button(
                    "📍 To Station",
                    "journey_to",
                    "primary",
                )
            ],
            [
                button(
                    "📅 Journey Date",
                    "journey_date",
                )
            ],
            [
                button(
                    "🚆 Select Train",
                    "journey_train",
                    "primary",
                )
            ],
            [
                button(
                    "💺 Select Class",
                    "journey_class",
                )
            ],
            [
                button(
                    "👤 Passenger",
                    "journey_passenger",
                )
            ],
            [
                button(
                    "🔔 Availability Alert",
                    "journey_alert",
                )
            ],
            [
                button(
                    "✅ Save Journey",
                    "save_journey",
                    "success",
                )
            ],
            [
                button(
                    "❌ Cancel",
                    "home",
                    "danger",
                )
            ],
        ]
    )


def class_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button("SL", "class_SL"),
                button("3A", "class_3A", "primary"),
                button("2A", "class_2A"),
            ],
            [
                button("1A", "class_1A"),
                button("CC", "class_CC"),
                button("EC", "class_EC"),
            ],
            [
                button("◀️ Back", "book_ticket"),
            ],
        ]
    )


def train_results(trains):

    rows = []

    for train in trains:

        rows.append(
            [
                button(
                    f"🚆 {train['number']} • {train['name']}",
                    f"train_{train['number']}",
                    "primary",
                )
            ]
        )

    rows.append(
        [
            button(
                "🔄 Refresh",
                "search_train",
            ),
            button(
                "🏠 Home",
                "home",
            ),
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )


def booking_summary_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button(
                    "💳 Continue to Payment",
                    "dummy_payment",
                    "success",
                )
            ],
            [
                button(
                    "✏️ Edit Journey",
                    "book_ticket",
                )
            ],
            [
                button(
                    "❌ Cancel",
                    "home",
                    "danger",
                )
            ],
        ]
    )


def payment_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button(
                    "💳 Pay ₹1450 (DEMO)",
                    "confirm_payment",
                    "success",
                )
            ],
            [
                button(
                    "❌ Cancel Payment",
                    "home",
                    "danger",
                )
            ],
        ]
    )


def after_booking_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button(
                    "📄 Booking Details",
                    "booking_details",
                    "primary",
                )
            ],
            [
                button(
                    "🚆 New Booking",
                    "book_ticket",
                    "success",
                )
            ],
            [
                button(
                    "🏠 Home",
                    "home",
                )
            ],
        ]
    )


def admin_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button("👥 Users", "admin_users", "primary"),
                button("📊 Statistics", "admin_stats"),
            ],
            [
                button(
                    "💬 Message User",
                    "admin_message",
                    "success",
                ),
                button(
                    "📢 Broadcast",
                    "admin_broadcast",
                ),
            ],
            [
                button("🚆 Journeys", "admin_journeys"),
                button("🔎 Monitoring", "admin_monitoring"),
            ],
            [
                button("📝 Logs", "admin_logs"),
                button("🔄 System", "admin_system"),
            ],
            [
                button("🏠 Home", "home"),
            ],
        ]
    )


def admin_back():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button(
                    "◀️ Admin Panel",
                    "admin_panel",
                    "primary",
                )
            ]
        ]
    )
