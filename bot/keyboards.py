from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def B(text, callback_data=None, style=None, url=None):
    data = {"text": text}

    if callback_data:
        data["callback_data"] = callback_data

    if style:
        data["style"] = style

    if url:
        data["url"] = url

    return InlineKeyboardButton(**data)


# ==========================================================
# MAIN MENU
# ==========================================================

def main_menu(user_id=None, admin_id=None):

    buttons = [
        [
            B("🚆 Search Train", "search_train", "primary"),
            B("👤 My Profile", "profile", "primary"),
        ],
        [
            B("🧳 My Journey", "book_ticket", "primary"),
            B("📅 My Bookings", "booking_details", "primary"),
        ],
        [
            B("🔔 Alerts", "alerts", "primary"),
            B("⚙️ Settings", "settings"),
        ],
    ]

    # ADMIN BUTTON ONLY FOR ADMIN
    if user_id is not None and admin_id is not None:
        if str(user_id) == str(admin_id):
            buttons.append([
                B("⚙️ Admin Panel", "admin_panel", "danger")
            ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ==========================================================
# HOME
# ==========================================================

def back_home():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                B("⬅️ Back to Home", "home", "primary")
            ]
        ]
    )


# ==========================================================
# PROFILE
# ==========================================================

def profile_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                B("➕ Add Passenger", "add_passenger", "success"),
            ],
            [
                B("👁 View Profile", "view_profile", "primary"),
                B("✏️ Edit", "edit_profile", "primary"),
            ],
            [
                B("🗑 Delete Profile", "delete_profile", "danger"),
            ],
            [
                B("⬅️ Home", "home", "primary")
            ],
        ]
    )


def gender_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                B("Male", "gender_male", "primary"),
                B("Female", "gender_female", "primary"),
            ],
            [
                B("Other", "gender_other", "primary")
            ],
        ]
    )


def berth_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                B("Lower", "berth_lower", "primary"),
                B("Middle", "berth_middle", "primary"),
            ],
            [
                B("Upper", "berth_upper", "primary"),
                B("Side Lower", "berth_sl", "primary"),
            ],
            [
                B("Side Upper", "berth_su", "primary"),
            ],
        ]
    )


# ==========================================================
# JOURNEY MENU
# ==========================================================

def journey_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                B("📍 From Station", "journey_from", "primary"),
                B("📍 To Station", "journey_to", "primary"),
            ],
            [
                B("📅 Journey Date", "journey_date", "primary"),
            ],
            [
                B("🚆 Search Trains", "journey_train", "success"),
            ],
            [
                B("💺 Select Class", "journey_class", "primary"),
                B("👤 Passenger", "journey_passenger", "primary"),
            ],
            [
                B("🔔 Availability Alert", "journey_alert", "primary"),
            ],
            [
                B("💾 Save Journey", "save_journey", "success"),
            ],
            [
                B("⬅️ Home", "home", "primary")
            ],
        ]
    )


# ==========================================================
# CLASS
# ==========================================================

def class_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                B("1A", "class_1A", "primary"),
                B("2A", "class_2A", "primary"),
            ],
            [
                B("3A", "class_3A", "primary"),
                B("SL", "class_SL", "primary"),
            ],
            [
                B("⬅️ Back", "book_ticket", "primary")
            ],
        ]
    )


# ==========================================================
# TRAIN RESULTS
# ==========================================================

def train_results(trains):

    buttons = []

    for train in trains:
        buttons.append([
            B(
                f"🚆 {train['number']} — {train['name']}",
                f"train_{train['number']}",
                "primary"
            )
        ])

    buttons.append([
        B("⬅️ Back", "book_ticket", "primary")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ==========================================================
# BOOKING SUMMARY
# ==========================================================

def booking_summary_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                B("💳 Continue Payment", "dummy_payment", "success")
            ],
            [
                B("❌ Cancel Booking", "cancel_booking", "danger")
            ],
        ]
    )


# ==========================================================
# PAYMENT
# ==========================================================

def payment_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                B("✅ Confirm Demo Payment", "confirm_payment", "success")
            ],
            [
                B("❌ Cancel", "cancel_booking", "danger")
            ],
        ]
    )


# ==========================================================
# AFTER BOOKING
# ==========================================================

def after_booking_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                B("📄 Booking Details", "booking_details", "primary")
            ],
            [
                B("🏠 Home", "home", "primary")
            ],
        ]
    )


# ==========================================================
# ADMIN MENU
# ==========================================================

def admin_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                B("📊 Stats", "admin_stats", "primary"),
                B("👥 Users", "admin_users", "primary"),
            ],
            [
                B("📢 Broadcast", "admin_broadcast", "success"),
                B("💬 Message User", "admin_message", "primary"),
            ],
            [
                B("🚆 Journeys", "admin_journeys", "primary"),
                B("🔔 Monitoring", "admin_monitoring", "primary"),
            ],
            [
                B("📋 Logs", "admin_logs"),
                B("⚙️ System Status", "admin_system", "primary"),
            ],
            [
                B("⬅️ Back Home", "home", "primary")
            ],
        ]
    )


# ==========================================================
# ADMIN BACK
# ==========================================================

def admin_back():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                B("⬅️ Admin Panel", "admin_panel", "primary")
            ],
            [
                B("🏠 Home", "home", "primary")
            ],
        ]
    )
