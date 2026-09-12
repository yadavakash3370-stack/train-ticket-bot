from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID

from bot.keyboards import (
    main_menu,
    back_home,
    profile_menu,
    gender_keyboard,
    berth_keyboard,
    journey_menu,
    class_keyboard,
    train_results,
    booking_summary_keyboard,
    payment_keyboard,
    after_booking_keyboard,
    admin_menu,
    admin_back,
)

from services.railway import search_trains
from services.booking import create_dummy_booking


router = Router()

users = {}
journeys = {}
bookings = {}
logs = []


# ==========================================================
# STATES
# ==========================================================

class ProfileStates(StatesGroup):
    waiting_name = State()
    waiting_age = State()


class JourneyStates(StatesGroup):
    waiting_from = State()
    waiting_to = State()
    waiting_date = State()


class AdminStates(StatesGroup):
    waiting_user_id = State()
    waiting_message = State()
    waiting_broadcast = State()


# ==========================================================
# HELPERS
# ==========================================================

def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)


def add_log(event, user_id):
    logs.append({
        "event": event,
        "user_id": user_id,
    })


def get_user(user_id):

    if user_id not in users:
        users[user_id] = {
            "telegram_id": user_id,
            "name": None,
            "age": None,
            "gender": None,
            "berth": None,
        }

    return users[user_id]


def get_journey(user_id):

    if user_id not in journeys:
        journeys[user_id] = {
            "source": None,
            "destination": None,
            "date": None,
            "train_number": None,
            "train_name": None,
            "travel_class": None,
            "passenger": None,
            "alert": False,
        }

    return journeys[user_id]


def home_keyboard(user_id):
    return main_menu(
        user_id=user_id,
        admin_id=ADMIN_ID
    )


# ==========================================================
# START
# ==========================================================

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):

    await state.clear()

    user_id = message.from_user.id

    get_user(user_id)

    add_log(
        "User started bot",
        user_id
    )

    await message.answer(
        "🚆 <b>TRAIN BOOKING ASSISTANT</b>\n\n"
        "Welcome!\n\n"
        "This is a dummy/testing version.\n"
        "Train availability and payment are simulated.\n\n"
        "Neeche menu se option select karo.",
        reply_markup=home_keyboard(user_id),
        parse_mode="HTML",
    )


# ==========================================================
# HOME
# ==========================================================

@router.callback_query(F.data == "home")
async def home(
    callback: CallbackQuery,
    state: FSMContext,
):

    await state.clear()

    await callback.message.edit_text(
        "🚆 <b>TRAIN BOOKING ASSISTANT</b>\n\n"
        "Main Menu",
        reply_markup=home_keyboard(callback.from_user.id),
        parse_mode="HTML",
    )

    await callback.answer()


# ==========================================================
# PROFILE
# ==========================================================

@router.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):

    user = get_user(callback.from_user.id)

    await callback.message.edit_text(
        "👤 <b>PASSENGER PROFILE</b>\n\n"
        f"Name: {user['name'] or 'Not set'}\n"
        f"Age: {user['age'] or 'Not set'}\n"
        f"Gender: {user['gender'] or 'Not set'}\n"
        f"Berth: {user['berth'] or 'Not set'}",
        reply_markup=profile_menu(),
        parse_mode="HTML",
    )

    await callback.answer()


@router.callback_query(F.data == "add_passenger")
async def add_passenger(
    callback: CallbackQuery,
    state: FSMContext,
):

    await state.set_state(ProfileStates.waiting_name)

    await callback.message.edit_text(
        "👤 <b>ADD PASSENGER</b>\n\n"
        "Full name enter karo.",
        parse_mode="HTML",
    )

    await callback.answer()


@router.message(ProfileStates.waiting_name)
async def receive_name(
    message: Message,
    state: FSMContext,
):

    if not message.text:
        await message.answer("Valid name enter karo.")
        return

    name = message.text.strip()

    if len(name) < 2:
        await message.answer("Valid name enter karo.")
        return

    get_user(message.from_user.id)["name"] = name

    await state.set_state(ProfileStates.waiting_age)

    await message.answer("Age enter karo.")


@router.message(ProfileStates.waiting_age)
async def receive_age(
    message: Message,
    state: FSMContext,
):

    try:
        age = int(message.text)

        if not 1 <= age <= 120:
            raise ValueError

    except (ValueError, TypeError):
        await message.answer("Valid age enter karo.")
        return

    get_user(message.from_user.id)["age"] = age

    await state.clear()

    await message.answer(
        "Gender select karo.",
        reply_markup=gender_keyboard(),
    )


@router.callback_query(F.data.startswith("gender_"))
async def gender(callback: CallbackQuery):

    value = callback.data.replace(
        "gender_",
        "",
    )

    get_user(
        callback.from_user.id
    )["gender"] = value.capitalize()

    await callback.message.edit_text(
        "🛏 <b>BERTH PREFERENCE</b>",
        reply_markup=berth_keyboard(),
        parse_mode="HTML",
    )

    await callback.answer()


@router.callback_query(F.data.startswith("berth_"))
async def berth(callback: CallbackQuery):

    mapping = {
        "berth_lower": "Lower",
        "berth_middle": "Middle",
        "berth_upper": "Upper",
        "berth_sl": "Side Lower",
        "berth_su": "Side Upper",
    }

    value = mapping.get(
        callback.data,
        "No Preference",
    )

    get_user(
        callback.from_user.id
    )["berth"] = value

    await callback.message.edit_text(
        "✅ <b>Passenger profile saved.</b>",
        reply_markup=profile_menu(),
        parse_mode="HTML",
    )

    await callback.answer()


@router.callback_query(F.data == "view_profile")
async def view_profile(callback: CallbackQuery):

    user = get_user(callback.from_user.id)

    await callback.message.edit_text(
        "👤 <b>PROFILE</b>\n\n"
        f"Name: {user['name'] or '-'}\n"
        f"Age: {user['age'] or '-'}\n"
        f"Gender: {user['gender'] or '-'}\n"
        f"Berth: {user['berth'] or '-'}",
        reply_markup=profile_menu(),
        parse_mode="HTML",
    )

    await callback.answer()


@router.callback_query(F.data == "edit_profile")
async def edit_profile(
    callback: CallbackQuery,
    state: FSMContext,
):

    await state.set_state(ProfileStates.waiting_name)

    await callback.message.edit_text(
        "✏️ New passenger name enter karo."
    )

    await callback.answer()


@router.callback_query(F.data == "delete_profile")
async def delete_profile(callback: CallbackQuery):

    user_id = callback.from_user.id

    users[user_id] = {
        "telegram_id": user_id,
        "name": None,
        "age": None,
        "gender": None,
        "berth": None,
    }

    await callback.message.edit_text(
        "🗑 Profile deleted.",
        reply_markup=profile_menu(),
    )

    await callback.answer()


# ==========================================================
# JOURNEY
# ==========================================================

@router.callback_query(F.data == "book_ticket")
async def book_ticket(callback: CallbackQuery):

    get_journey(callback.from_user.id)

    await callback.message.edit_text(
        "🚆 <b>NEW JOURNEY</b>\n\n"
        "Journey details configure karo.",
        reply_markup=journey_menu(),
        parse_mode="HTML",
    )

    await callback.answer()


@router.callback_query(F.data == "journey_from")
async def journey_from(
    callback: CallbackQuery,
    state: FSMContext,
):

    await state.set_state(JourneyStates.waiting_from)

    await callback.message.edit_text(
        "📍 <b>FROM STATION</b>\n\n"
        "Station code enter karo.\n"
        "Example: PRYJ",
        parse_mode="HTML",
    )

    await callback.answer()


@router.message(JourneyStates.waiting_from)
async def receive_from(
    message: Message,
    state: FSMContext,
):

    if not message.text:
        await message.answer("Valid station code enter karo.")
        return

    value = message.text.strip().upper()

    if len(value) < 2:
        await message.answer("Valid station code enter karo.")
        return

    get_journey(
        message.from_user.id
    )["source"] = value

    await state.clear()

    await message.answer(
        f"✅ From: <b>{value}</b>",
        reply_markup=journey_menu(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "journey_to")
async def journey_to(
    callback: CallbackQuery,
    state: FSMContext,
):

    await state.set_state(JourneyStates.waiting_to)

    await callback.message.edit_text(
        "📍 <b>TO STATION</b>\n\n"
        "Station code enter karo.\n"
        "Example: NDLS",
        parse_mode="HTML",
    )

    await callback.answer()


@router.message(JourneyStates.waiting_to)
async def receive_to(
    message: Message,
    state: FSMContext,
):

    if not message.text:
        await message.answer("Valid station code enter karo.")
        return

    value = message.text.strip().upper()

    if len(value) < 2:
        await message.answer("Valid station code enter karo.")
        return

    get_journey(
        message.from_user.id
    )["destination"] = value

    await state.clear()

    await message.answer(
        f"✅ To: <b>{value}</b>",
        reply_markup=journey_menu(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "journey_date")
async def journey_date(
    callback: CallbackQuery,
    state: FSMContext,
):

    await state.set_state(JourneyStates.waiting_date)

    await callback.message.edit_text(
        "📅 <b>JOURNEY DATE</b>\n\n"
        "Format: DD-MM-YYYY\n\n"
        "Example: 20-10-2026",
        parse_mode="HTML",
    )

    await callback.answer()


@router.message(JourneyStates.waiting_date)
async def receive_date(
    message: Message,
    state: FSMContext,
):

    if not message.text:
        await message.answer(
            "Date DD-MM-YYYY format mein enter karo."
        )
        return

    value = message.text.strip()

    parts = value.split("-")

    if len(parts) != 3:
        await message.answer(
            "Date DD-MM-YYYY format mein enter karo."
        )
        return

    get_journey(
        message.from_user.id
    )["date"] = value

    await state.clear()

    await message.answer(
        f"✅ Date: <b>{value}</b>",
        reply_markup=journey_menu(),
        parse_mode="HTML",
    )


# ==========================================================
# CLASS
# ==========================================================

@router.callback_query(F.data == "journey_class")
async def journey_class(callback: CallbackQuery):

    await callback.message.edit_text(
        "💺 <b>SELECT CLASS</b>",
        reply_markup=class_keyboard(),
        parse_mode="HTML",
    )

    await callback.answer()


@router.callback_query(F.data.startswith("class_"))
async def select_class(callback: CallbackQuery):

    value = callback.data.replace(
        "class_",
        "",
    )

    get_journey(
        callback.from_user.id
    )["travel_class"] = value

    await callback.message.edit_text(
        f"✅ Class: <b>{value}</b>",
        reply_markup=journey_menu(),
        parse_mode="HTML",
    )

    await callback.answer()


# ==========================================================
# TRAIN SEARCH
# ==========================================================

@router.callback_query(F.data == "search_train")
async def search_train(callback: CallbackQuery):

    journey = get_journey(callback.from_user.id)

    if not journey["source"]:
        await callback.message.edit_text(
            "⚠️ Pehle From station set karo.",
            reply_markup=journey_menu(),
        )
        await callback.answer()
        return

    if not journey["destination"]:
        await callback.message.edit_text(
            "⚠️ Pehle To station set karo.",
            reply_markup=journey_menu(),
        )
        await callback.answer()
        return

    if not journey["date"]:
        await callback.message.edit_text(
            "⚠️ Pehle journey date set karo.",
            reply_markup=journey_menu(),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "🔎 Searching trains..."
    )

    trains = await search_trains(
        journey["source"],
        journey["destination"],
        journey["date"],
    )

    if not trains:
        await callback.message.edit_text(
            "❌ No trains found.",
            reply_markup=journey_menu(),
        )
        await callback.answer()
        return

    text = "🔎 <b>TRAIN RESULTS</b>\n\n"

    for train in trains:
        text += (
            f"🚆 <b>{train['number']}</b> "
            f"{train['name']}\n"
            f"🕐 {train['departure']} → "
            f"{train['arrival']}\n"
            f"💺 Seats: {train['seats']}\n"
            f"💰 Fare: ₹{train['fare']}\n\n"
        )

    await callback.message.edit_text(
        text,
        reply_markup=train_results(trains),
        parse_mode="HTML",
    )

    await callback.answer()


@router.callback_query(F.data == "journey_train")
async def journey_train(callback: CallbackQuery):
    await search_train(callback)
    # =========================
# PART 2/2
# =========================

from services.booking import create_dummy_booking


# =========================
# TRAIN SELECTION
# =========================

@router.callback_query(F.data.startswith("train_"))
async def select_train(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    train_id = callback.data.replace("train_", "", 1)

    journey = get_journey(user_id)

    if not journey:
        await callback.answer("Journey nahi mili.", show_alert=True)
        return

    journey["train_id"] = train_id

    await callback.message.edit_text(
        "👤 <b>Passenger select karein</b>\n\n"
        "Ab passenger ki details enter karni hongi.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [B("👤 Passenger Details", "journey_passenger", "primary")],
                [B("⬅️ Back", "journey_train")],
                [B("🏠 Home", "home")]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# PASSENGER
# =========================

@router.callback_query(F.data == "journey_passenger")
async def journey_passenger(callback: CallbackQuery, state: FSMContext):
    await state.set_state(JourneyStates.passenger)

    await callback.message.edit_text(
        "👤 <b>Passenger Details</b>\n\n"
        "Is format mein bhejiye:\n\n"
        "<code>Name, Age</code>\n\n"
        "Example:\n"
        "<code>Akash Yadav, 18</code>",
        parse_mode="HTML"
    )

    await callback.answer()


@router.message(JourneyStates.passenger)
async def passenger_received(message: Message, state: FSMContext):
    text = message.text.strip()

    if "," not in text:
        await message.answer(
            "❌ Format galat hai.\n\n"
            "Example: <code>Akash Yadav, 18</code>",
            parse_mode="HTML"
        )
        return

    name, age = text.split(",", 1)

    name = name.strip()
    age = age.strip()

    if not name or not age.isdigit():
        await message.answer(
            "❌ Please valid name aur age bhejiye.\n\n"
            "Example: <code>Akash Yadav, 18</code>",
            parse_mode="HTML"
        )
        return

    user_id = message.from_user.id
    journey = get_journey(user_id)

    if not journey:
        await message.answer(
            "❌ Journey nahi mili.",
            reply_markup=home_keyboard(user_id)
        )
        await state.clear()
        return

    journey["passenger"] = {
        "name": name,
        "age": int(age)
    }

    await state.clear()

    await message.answer(
        "👤 Passenger saved.\n\n"
        f"<b>Name:</b> {name}\n"
        f"<b>Age:</b> {age}\n\n"
        "Ab journey ko save kar sakte hain.",
        reply_markup=journey_menu(),
        parse_mode="HTML"
    )


# =========================
# ALERT
# =========================

@router.callback_query(F.data == "journey_alert")
async def journey_alert(callback: CallbackQuery):
    user_id = callback.from_user.id
    journey = get_journey(user_id)

    if not journey:
        await callback.answer("Journey nahi mili.", show_alert=True)
        return

    journey["alert"] = not journey.get("alert", False)

    status = "ON" if journey["alert"] else "OFF"

    await callback.message.edit_text(
        "🔔 <b>Journey Alert</b>\n\n"
        f"Alert status: <b>{status}</b>",
        reply_markup=journey_menu(),
        parse_mode="HTML"
    )

    await callback.answer(f"Alert {status}")


# =========================
# SAVE JOURNEY
# =========================

@router.callback_query(F.data == "save_journey")
async def save_journey(callback: CallbackQuery):
    user_id = callback.from_user.id
    journey = get_journey(user_id)

    if not journey:
        await callback.answer(
            "Pehle journey create karein.",
            show_alert=True
        )
        return

    required = [
        "source",
        "destination",
        "date",
        "travel_class",
        "train_id",
        "passenger"
    ]

    missing = [x for x in required if not journey.get(x)]

    if missing:
        await callback.answer(
            "Journey abhi complete nahi hai.",
            show_alert=True
        )
        return

    users[user_id]["journeys"] = users[user_id].get("journeys", [])

    saved = dict(journey)
    saved["id"] = str(len(users[user_id]["journeys"]) + 1)

    users[user_id]["journeys"].append(saved)

    add_log(
        user_id,
        "journey_saved",
        f"{saved['source']} -> {saved['destination']}"
    )

    await callback.message.edit_text(
        "✅ <b>Journey Saved</b>\n\n"
        f"🚉 {saved['source']} → {saved['destination']}\n"
        f"📅 {saved['date']}\n"
        f"🎫 {saved['travel_class']}\n\n"
        "Journey successfully save ho gayi.",
        reply_markup=home_keyboard(user_id),
        parse_mode="HTML"
    )

    await callback.answer("Journey saved")


# =========================
# MY JOURNEYS
# =========================

@router.callback_query(F.data == "book_ticket")
async def my_journeys(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)

    saved_journeys = user.get("journeys", [])

    if not saved_journeys:
        await callback.message.edit_text(
            "🧳 <b>My Journey</b>\n\n"
            "Abhi koi saved journey nahi hai.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [B("➕ New Journey", "search_train", "primary")],
                    [B("🏠 Home", "home")]
                ]
            ),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    text = "🧳 <b>My Journeys</b>\n\n"

    for i, journey in enumerate(saved_journeys, start=1):
        text += (
            f"<b>{i}. {journey.get('source', '-')} → "
            f"{journey.get('destination', '-')}</b>\n"
            f"📅 {journey.get('date', '-')}\n"
            f"🎫 {journey.get('travel_class', '-')}\n\n"
        )

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [B("➕ New Journey", "search_train", "primary")],
                [B("🏠 Home", "home")]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# ALERTS
# =========================

@router.callback_query(F.data == "alerts")
async def alerts(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)

    active_alerts = []

    for journey in user.get("journeys", []):
        if journey.get("alert"):
            active_alerts.append(journey)

    if not active_alerts:
        text = (
            "🔔 <b>Alerts</b>\n\n"
            "Abhi koi active journey alert nahi hai."
        )
    else:
        text = "🔔 <b>Active Alerts</b>\n\n"

        for journey in active_alerts:
            text += (
                f"🚆 {journey.get('source')} → "
                f"{journey.get('destination')}\n"
                f"📅 {journey.get('date')}\n\n"
            )

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [B("🏠 Home", "home")]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# SETTINGS
# =========================

@router.callback_query(F.data == "settings")
async def settings(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚙️ <b>Settings</b>\n\n"
        "Bot settings yahan manage ki ja sakti hain.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [B("🔔 Notifications", "alerts", "primary")],
                [B("⬅️ Home", "home")]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# DUMMY PAYMENT
# =========================

@router.callback_query(F.data == "dummy_payment")
async def dummy_payment(callback: CallbackQuery):
    user_id = callback.from_user.id
    journey = get_journey(user_id)

    if not journey:
        await callback.answer(
            "Journey nahi mili.",
            show_alert=True
        )
        return

    passenger = journey.get("passenger", {})

    await callback.message.edit_text(
        "💳 <b>Dummy Payment</b>\n\n"
        "Ye testing/demo payment hai.\n"
        "Koi real payment nahi hogi.\n\n"
        f"🚉 <b>Route:</b> {journey.get('source')} → "
        f"{journey.get('destination')}\n"
        f"📅 <b>Date:</b> {journey.get('date')}\n"
        f"🎫 <b>Class:</b> {journey.get('travel_class')}\n"
        f"👤 <b>Passenger:</b> {passenger.get('name', '-')}\n\n"
        "Payment confirm karne ke liye button dabayein.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [B("✅ Pay & Book Demo", "confirm_payment", "success")],
                [B("❌ Cancel", "cancel_booking", "danger")]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# CONFIRM PAYMENT / BOOKING
# =========================

@router.callback_query(F.data == "confirm_payment")
async def confirm_payment(callback: CallbackQuery):
    user_id = callback.from_user.id
    journey = get_journey(user_id)

    if not journey:
        await callback.answer(
            "Journey nahi mili.",
            show_alert=True
        )
        return

    try:
        booking = create_dummy_booking(
            user_id,
            journey
        )
    except Exception as e:
        add_log(user_id, "booking_error", str(e))

        await callback.message.edit_text(
            "❌ Booking create nahi ho saki.\n\n"
            "Please dobara try karein.",
            reply_markup=home_keyboard(user_id)
        )

        await callback.answer()
        return

    bookings[user_id] = booking

    add_log(
        user_id,
        "booking_created",
        booking.get("pnr", "unknown")
    )

    await callback.message.edit_text(
        "🎉 <b>Demo Ticket Booked!</b>\n\n"
        f"🎫 <b>PNR:</b> <code>{booking.get('pnr')}</code>\n"
        f"🚆 <b>Train:</b> {booking.get('train_name')}\n"
        f"🔢 <b>Train No:</b> {booking.get('train_number')}\n"
        f"🚉 <b>Route:</b> {booking.get('source')} → "
        f"{booking.get('destination')}\n"
        f"📅 <b>Date:</b> {booking.get('date')}\n"
        f"💺 <b>Class:</b> {booking.get('travel_class')}\n"
        f"👤 <b>Passenger:</b> "
        f"{booking.get('passenger', {}).get('name', '-')}\n\n"
        "⚠️ Ye sirf demo/testing booking hai.",
        reply_markup=after_booking_keyboard(),
        parse_mode="HTML"
    )

    await callback.answer("Demo booking successful")


# =========================
# CANCEL BOOKING
# =========================

@router.callback_query(F.data == "cancel_booking")
async def cancel_booking(callback: CallbackQuery):
    user_id = callback.from_user.id

    add_log(
        user_id,
        "booking_cancelled",
        "dummy payment cancelled"
    )

    await callback.message.edit_text(
        "❌ <b>Booking Cancelled</b>\n\n"
        "Demo booking process cancel kar diya gaya.",
        reply_markup=home_keyboard(user_id),
        parse_mode="HTML"
    )

    await callback.answer("Cancelled")


# =========================
# BOOKING DETAILS
# =========================

@router.callback_query(F.data == "booking_details")
async def booking_details(callback: CallbackQuery):
    user_id = callback.from_user.id
    booking = bookings.get(user_id)

    if not booking:
        await callback.message.edit_text(
            "📅 <b>My Bookings</b>\n\n"
            "Abhi koi booking available nahi hai.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [B("🚆 Search Train", "search_train", "primary")],
                    [B("🏠 Home", "home")]
                ]
            ),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    passenger = booking.get("passenger", {})

    await callback.message.edit_text(
        "🎫 <b>My Booking</b>\n\n"
        f"🔖 <b>PNR:</b> <code>{booking.get('pnr')}</code>\n"
        f"🚆 <b>Train:</b> {booking.get('train_name')}\n"
        f"🔢 <b>Train No:</b> {booking.get('train_number')}\n"
        f"🚉 <b>From:</b> {booking.get('source')}\n"
        f"🏁 <b>To:</b> {booking.get('destination')}\n"
        f"📅 <b>Date:</b> {booking.get('date')}\n"
        f"💺 <b>Class:</b> {booking.get('travel_class')}\n"
        f"👤 <b>Passenger:</b> {passenger.get('name', '-')}\n"
        f"📌 <b>Status:</b> {booking.get('status', 'CONFIRMED')}\n\n"
        "⚠️ Demo booking only.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [B("🏠 Home", "home")]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================================================
# ADMIN PANEL
# =========================================================

@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "❌ Admin access required.",
            show_alert=True
        )
        return

    await callback.message.edit_text(
        "⚙️ <b>Admin Panel</b>\n\n"
        "Admin controls select karein.",
        reply_markup=admin_menu(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# ADMIN STATS
# =========================

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return

    total_users = len(users)
    total_journeys = sum(
        len(user.get("journeys", []))
        for user in users.values()
    )
    total_bookings = len(bookings)
    total_logs = len(logs)

    await callback.message.edit_text(
        "📊 <b>Bot Statistics</b>\n\n"
        f"👥 Users: <b>{total_users}</b>\n"
        f"🧳 Saved Journeys: <b>{total_journeys}</b>\n"
        f"🎫 Bookings: <b>{total_bookings}</b>\n"
        f"📝 Logs: <b>{total_logs}</b>",
        reply_markup=admin_back(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# ADMIN USERS
# =========================

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return

    if not users:
        text = "👥 <b>Users</b>\n\nNo users found."
    else:
        text = "👥 <b>Users</b>\n\n"

        for i, (user_id, user) in enumerate(
            users.items(),
            start=1
        ):
            name = user.get("name") or "Unknown"

            text += (
                f"{i}. <b>{name}</b>\n"
                f"ID: <code>{user_id}</code>\n\n"
            )

    await callback.message.edit_text(
        text,
        reply_markup=admin_back(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# ADMIN MESSAGE
# =========================

@router.callback_query(F.data == "admin_message")
async def admin_message(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return

    await state.set_state(AdminStates.message_user)

    await callback.message.edit_text(
        "📩 <b>Message User</b>\n\n"
        "Format:\n"
        "<code>USER_ID | MESSAGE</code>\n\n"
        "Example:\n"
        "<code>123456789 | Hello</code>",
        parse_mode="HTML"
    )

    await callback.answer()


@router.message(AdminStates.message_user)
async def admin_message_received(
    message: Message,
    state: FSMContext
):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    text = message.text.strip()

    if "|" not in text:
        await message.answer(
            "❌ Format galat hai.\n\n"
            "<code>USER_ID | MESSAGE</code>",
            parse_mode="HTML"
        )
        return

    user_id_text, msg_text = text.split("|", 1)

    try:
        target_user_id = int(user_id_text.strip())
    except ValueError:
        await message.answer("❌ Invalid USER_ID.")
        return

    msg_text = msg_text.strip()

    if not msg_text:
        await message.answer("❌ Message empty hai.")
        return

    try:
        await message.bot.send_message(
            target_user_id,
            f"📩 <b>Admin Message</b>\n\n{msg_text}",
            parse_mode="HTML"
        )

        await message.answer(
            "✅ Message successfully sent.",
            reply_markup=admin_menu()
        )

        add_log(
            message.from_user.id,
            "admin_message",
            str(target_user_id)
        )

    except Exception as e:
        await message.answer(
            f"❌ Message send failed.\n\n<code>{e}</code>",
            parse_mode="HTML"
        )

    await state.clear()


# =========================
# ADMIN BROADCAST
# =========================

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(
    callback: CallbackQuery,
    state: FSMContext
):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return

    await state.set_state(AdminStates.broadcast)

    await callback.message.edit_text(
        "📢 <b>Broadcast</b>\n\n"
        "Jo message sabhi registered users ko bhejna hai "
        "wo send karein.",
        parse_mode="HTML"
    )

    await callback.answer()


@router.message(AdminStates.broadcast)
async def admin_broadcast_received(
    message: Message,
    state: FSMContext
):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    broadcast_text = message.text.strip()

    if not broadcast_text:
        await message.answer("❌ Message empty hai.")
        return

    success = 0
    failed = 0

    for user_id in list(users.keys()):
        try:
            await message.bot.send_message(
                user_id,
                f"📢 <b>Announcement</b>\n\n{broadcast_text}",
                parse_mode="HTML"
            )
            success += 1

        except Exception:
            failed += 1

    add_log(
        message.from_user.id,
        "broadcast",
        f"success={success}, failed={failed}"
    )

    await message.answer(
        "📢 <b>Broadcast Complete</b>\n\n"
        f"✅ Sent: {success}\n"
        f"❌ Failed: {failed}",
        reply_markup=admin_menu(),
        parse_mode="HTML"
    )

    await state.clear()


# =========================
# ADMIN JOURNEYS
# =========================

@router.callback_query(F.data == "admin_journeys")
async def admin_journeys(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return

    rows = []

    for user_id, user in users.items():
        for journey in user.get("journeys", []):
            rows.append(
                f"👤 <code>{user_id}</code>\n"
                f"🚉 {journey.get('source')} → "
                f"{journey.get('destination')}\n"
                f"📅 {journey.get('date')}\n"
            )

    if not rows:
        text = "🧳 <b>All Journeys</b>\n\nNo journeys found."
    else:
        text = (
            "🧳 <b>All Journeys</b>\n\n"
            + "\n".join(rows)
        )

    await callback.message.edit_text(
        text,
        reply_markup=admin_back(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# ADMIN MONITORING
# =========================

@router.callback_query(F.data == "admin_monitoring")
async def admin_monitoring(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return

    active_alerts = 0

    for user in users.values():
        for journey in user.get("journeys", []):
            if journey.get("alert"):
                active_alerts += 1

    await callback.message.edit_text(
        "📡 <b>Monitoring</b>\n\n"
        f"🔔 Active alerts: <b>{active_alerts}</b>\n"
        f"👥 Users monitored: <b>{len(users)}</b>\n\n"
        "Railway monitoring is currently running in "
        "demo mode.",
        reply_markup=admin_back(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# ADMIN LOGS
# =========================

@router.callback_query(F.data == "admin_logs")
async def admin_logs(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return

    if not logs:
        text = "📝 <b>Logs</b>\n\nNo logs available."
    else:
        recent_logs = logs[-20:]

        text = "📝 <b>Recent Logs</b>\n\n"

        for item in recent_logs:
            text += (
                f"• <code>{item.get('user_id')}</code> "
                f"{item.get('action')}\n"
                f"{item.get('details', '')}\n\n"
            )

    await callback.message.edit_text(
        text,
        reply_markup=admin_back(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# ADMIN SYSTEM
# =========================

@router.callback_query(F.data == "admin_system")
async def admin_system(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied.", show_alert=True)
        return

    await callback.message.edit_text(
        "🖥 <b>System</b>\n\n"
        "Bot status: <b>ONLINE</b>\n"
        "Storage: <b>In-Memory</b>\n"
        "Database: <b>Not Connected</b>\n"
        "Mode: <b>Demo</b>",
        reply_markup=admin_back(),
        parse_mode="HTML"
    )

    await callback.answer()
