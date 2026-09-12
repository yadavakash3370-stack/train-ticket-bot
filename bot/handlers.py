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


def is_admin(user_id):
    return user_id == ADMIN_ID


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
        user_id,
    )

    await message.answer(
        "🚆 <b>TRAIN BOOKING ASSISTANT</b>\n\n"
        "Welcome!\n\n"
        "This is a dummy/testing version.\n"
        "Train availability and payment are simulated.\n\n"
        "Neeche menu se option select karo.",
        reply_markup=main_menu(),
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
        reply_markup=main_menu(),
        parse_mode="HTML",
    )

    await callback.answer()


# ==========================================================
# PROFILE
# ==========================================================

@router.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):

    user = get_user(
        callback.from_user.id
    )

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

    await state.set_state(
        ProfileStates.waiting_name
    )

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

    name = message.text.strip()

    if len(name) < 2:

        await message.answer(
            "Valid name enter karo."
        )
        return

    get_user(
        message.from_user.id
    )["name"] = name

    await state.set_state(
        ProfileStates.waiting_age
    )

    await message.answer(
        "Age enter karo."
    )


@router.message(ProfileStates.waiting_age)
async def receive_age(
    message: Message,
    state: FSMContext,
):

    try:
        age = int(message.text)

        if not 1 <= age <= 120:
            raise ValueError

    except ValueError:

        await message.answer(
            "Valid age enter karo."
        )
        return

    get_user(
        message.from_user.id
    )["age"] = age

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

    user = get_user(
        callback.from_user.id
    )

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

    await state.set_state(
        ProfileStates.waiting_name
    )

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

    get_journey(
        callback.from_user.id
    )

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

    await state.set_state(
        JourneyStates.waiting_from
    )

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

    value = message.text.strip().upper()

    if len(value) < 2:

        await message.answer(
            "Valid station code enter karo."
        )
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

    await state.set_state(
        JourneyStates.waiting_to
    )

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

    value = message.text.strip().upper()

    if len(value) < 2:

        await message.answer(
            "Valid station code enter karo."
        )
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

    await state.set_state(
        JourneyStates.waiting_date
    )

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

    journey = get_journey(
        callback.from_user.id
    )

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


@router.callback_query(F.data.startswith("train_"))
async def select_train(callback: CallbackQuery):

    train_number = callback.data.replace(
        "train_",
        "",
    )

    journey = get_journey(
        callback.from_user.id
    )

    trains = await search_trains(
        journey["source"],
        journey["destination"],
        journey["date"],
    )

    for train in trains:

        if train["number"] == train_number:

            journey["train_number"] = train["number"]
            journey["train_name"] = train["name"]

            await callback.message.edit_text(
                "🚆 <b>TRAIN SELECTED</b>\n\n"
                f"{train['number']} — {train['name']}\n"
                f"🕐 {train['departure']} → "
                f"{train['arrival']}\n"
                f"💺 Seats: {train['seats']}\n"
                f"💰 Fare: ₹{train['fare']}",
                reply_markup=journey_menu(),
                parse_mode="HTML",
            )

            await callback.answer()
            return

    await callback.answer(
        "Train not found.",
        show_alert=True,
    )


# ==========================================================
# PASSENGER
# ==========================================================

@router.callback_query(F.data == "journey_passenger")
async def journey_passenger(callback: CallbackQuery):

    user = get_user(
        callback.from_user.id
    )

    if not user["name"]:

        await callback.message.edit_text(
            "⚠️ Pehle passenger profile create karo.",
            reply_markup=profile_menu(),
        )

        await callback.answer()
        return

    get_journey(
        callback.from_user.id
    )["passenger"] = user["name"]

    await callback.message.edit_text(
        "👤 <b>PASSENGER SELECTED</b>\n\n"
        f"Name: {user['name']}\n"
        f"Age: {user['age']}\n"
        f"Gender: {user['gender']}\n"
        f"Berth: {user['berth']}",
        reply_markup=journey_menu(),
        parse_mode="HTML",
    )

    await callback.answer()


# ==========================================================
# ALERT
# ==========================================================

@router.callback_query(F.data == "journey_alert")
async def journey_alert(callback: CallbackQuery):

    journey = get_journey(
        callback.from_user.id
    )

    journey["alert"] = not journey["alert"]

    status = (
        "🟢 ON"
        if journey["alert"]
        else "🔴 OFF"
    )

    await callback.message.edit_text(
        f"🔔 Availability Alert: <b>{status}</b>",
        reply_markup=journey_menu(),
        parse_mode="HTML",
    )

    await callback.answer()


# ==========================================================
# SAVE JOURNEY
# ==========================================================

@router.callback_query(F.data == "save_journey")
async def save_journey(callback: CallbackQuery):

    journey = get_journey(
        callback.from_user.id
    )

    required = [
        journey["source"],
        journey["destination"],
        journey["date"],
        journey["train_number"],
        journey["travel_class"],
        journey["passenger"],
    ]

    if any(value is None for value in required):

        await callback.answer(
            "Journey details incomplete.",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        "✅ <b>JOURNEY SAVED</b>\n\n"
        f"📍 {journey['source']} → "
        f"{journey['destination']}\n"
        f"📅 {journey['date']}\n"
        f"🚆 {journey['train_name']}\n"
        f"💺 {journey['travel_class']}\n"
        f"👤 {journey['passenger']}\n\n"
        "Ab booking continue kar sakte ho.",
        reply_markup=journey_menu(),
        parse_mode="HTML",
    )

    add_log(
        "Journey saved",
        callback.from_user.id,
    )

    await callback.answer()


# ==========================================================
# MY JOURNEYS
# ==========================================================

@router.callback_query(F.data == "my_journeys")
async def my_journeys(callback: CallbackQuery):

    journey = journeys.get(
        callback.from_user.id
    )

    if not journey or not journey.get("source"):

        await callback.message.edit_text(
            "📋 No saved journey.",
            reply_markup=back_home(),
        )

        await callback.answer()
        return

    await callback.message.edit_text(
        "📋 <b>MY JOURNEY</b>\n\n"
        f"📍 {journey['source']} → "
        f"{journey['destination']}\n"
        f"📅 {journey['date']}\n"
        f"🚆 {journey['train_name'] or '-'}\n"
        f"💺 {journey['travel_class'] or '-'}\n"
        f"👤 {journey['passenger'] or '-'}",
        reply_markup=back_home(),
        parse_mode="HTML",
    )

    await callback.answer()


# ==========================================================
# ALERTS
# ==========================================================

@router.callback_query(F.data == "alerts")
async def alerts(callback: CallbackQuery):

    journey = journeys.get(
        callback.from_user.id
    )

    status = (
        "🟢 Monitoring ON"
        if journey and journey.get("alert")
        else "🔴 Monitoring OFF"
    )

    await callback.message.edit_text(
        f"🔔 <b>MY ALERTS</b>\n\n{status}",
        reply_markup=back_home(),
        parse_mode="HTML",
    )

    await callback.answer()


# ==========================================================
# SETTINGS
# ==========================================================

@router.callback_query(F.data == "settings")
async def settings(callback: CallbackQuery):

    await callback.message.edit_text(
        "⚙️ <b>SETTINGS</b>\n\n"
        "Notifications: Enabled\n"
        "Database: Temporary Memory\n"
        "Railway API: Dummy\n"
        "Payment: Demo",
        reply_markup=back_home(),
        parse_mode="HTML",
    )

    await callback.answer()


# ==========================================================
# PAYMENT
# ==========================================================

@router.callback_query(F.data == "dummy_payment")
async def dummy_payment(callback: CallbackQuery):

    journey = get_journey(
        callback.from_user.id
    )

    await callback.message.edit_text(
        "💳 <b>DEMO PAYMENT</b>\n\n"
        f"🚆 {journey['train_name']}\n"
        f"💺 Class: {journey['travel_class']}\n"
        f"👤 {journey['passenger']}\n\n"
        "Amount: <b>₹1450</b>\n\n"
        "⚠️ No real payment will happen.",
        reply_markup=payment_keyboard(),
        parse_mode="HTML",
    )

    await callback.answer()


@router.callback_query(F.data == "confirm_payment")
async def confirm_payment(callback: CallbackQuery):

    journey = get_journey(
        callback.from_user.id
    )

    booking = await create_dummy_booking(
        callback.from_user.id,
        journey,
    )

    bookings[
        callback.from_user.id
    ] = booking

    await callback.message.edit_text(
        "✅ <b>BOOKING CONFIRMED</b>\n\n"
        f"🚆 {booking['train_number']} — "
        f"{booking['train_name']}\n"
        f"📍 {booking['source']} → "
        f"{booking['destination']}\n"
        f"📅 {booking['date']}\n"
        f"💺 {booking['travel_class']}\n"
        f"👤 {booking['passenger']}\n\n"
        f"🎫 PNR: <code>{booking['pnr']}</code>\n"
        f"💳 TXN: <code>{booking['transaction_id']}</code>\n\n"
        "🧪 DEMO BOOKING",
        reply_markup=after_booking_keyboard(),
        parse_mode="HTML",
    )

    add_log(
        "Demo booking confirmed",
        callback.from_user.id,
    )

    await callback.answer(
        "Demo payment successful!"
    )


@router.callback_query(F.data == "booking_details")
async def booking_details(callback: CallbackQuery):

    booking = bookings.get(
        callback.from_user.id
    )

    if not booking:

        await callback.answer(
            "No booking found.",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        "📄 <b>BOOKING DETAILS</b>\n\n"
        f"Status: 🟢 {booking['status']}\n"
        f"PNR: <code>{booking['pnr']}</code>\n"
        f"Train: {booking['train_number']} "
        f"{booking['train_name']}\n"
        f"Route: {booking['source']} → "
        f"{booking['destination']}\n"
        f"Date: {booking['date']}\n"
        f"Class: {booking['travel_class']}\n"
        f"Passenger: {booking['passenger']}",
        reply_markup=back_home(),
        parse_mode="HTML",
    )

    await callback.answer()


# ==========================================================
# ADMIN PANEL
# ==========================================================

@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):

        await callback.answer(
            "Access denied.",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        "⚙️ <b>ADMIN PANEL</b>\n\n"
        "Bot Control Center",
        reply_markup=admin_menu(),
        parse_mode="HTML",
    )

    await callback.answer()


@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):

        await callback.answer(
            "Access denied.",
            show_alert=True,
        )
        return

    if not users:

        text = "👥 No users."

    else:

        text = "👥 <b>USERS</b>\n\n"

        for user_id, user in list(users.items())[:20]:

            text += (
                f"👤 {user['name'] or 'No name'}\n"
                f"🆔 <code>{user_id}</code>\n\n"
            )

    await callback.message.edit_text(
        text,
        reply_markup=admin_back(),
        parse_mode="HTML",
    )

    await callback.answer()


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):

        await callback.answer(
            "Access denied.",
            show_alert=True,
        )
        return

    active_alerts = sum(
        1
        for journey in journeys.values()
        if journey.get("alert")
    )

    await callback.message.edit_text(
        "📊 <b>STATISTICS</b>\n\n"
        f"👥 Users: {len(users)}\n"
        f"🚆 Journeys: {len(journeys)}\n"
        f"🎫 Bookings: {len(bookings)}\n"
        f"🔔 Active Alerts: {active_alerts}\n"
        f"📝 Logs: {len(logs)}",
        reply_markup=admin_back(),
        parse_mode="HTML",
    )

    await callback.answer()

# ==========================================================
# ADMIN MESSAGE USER
# ==========================================================

@router.callback_query(F.data == "admin_message")
async def admin_message(
    callback: CallbackQuery,
    state: FSMContext,
):

    if not is_admin(callback.from_user.id):

        await callback.answer(
            "Access denied.",
            show_alert=True,
        )
        return

    await state.set_state(
        AdminStates.waiting_user_id
    )

    await callback.message.edit_text(
        "💬 <b>MESSAGE USER</b>\n\n"
        "Telegram numeric User ID enter karo.",
        parse_mode="HTML",
    )

    await callback.answer()


@router.message(AdminStates.waiting_user_id)
async def admin_user_id(
    message: Message,
    state: FSMContext,
):

    try:
        target_id = int(
            message.text.strip()
        )
    except ValueError:

        await message.answer(
            "Numeric Telegram User ID enter karo."
        )
        return

    if target_id not in users:

        await message.answer(
            "❌ User registered nahi hai."
        )

        await state.clear()
        return

    await state.update_data(
        target_id=target_id
    )

    await state.set_state(
        AdminStates.waiting_message
    )

    await message.answer(
        "💬 Message type karo:"
    )


@router.message(AdminStates.waiting_message)
async def admin_send_message(
    message: Message,
    state: FSMContext,
    bot,
):

    data = await state.get_data()

    target_id = data["target_id"]

    try:

        await bot.send_message(
            target_id,
            "📩 <b>Message from Admin</b>\n\n"
            + message.text,
            parse_mode="HTML",
        )

        await message.answer(
            "✅ Message sent."
        )

    except Exception as error:

        await message.answer(
            f"❌ Failed:\n{error}"
        )

    await state.clear()


# ==========================================================
# ADMIN BROADCAST
# ==========================================================

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(
    callback: CallbackQuery,
    state: FSMContext,
):

    if not is_admin(callback.from_user.id):

        await callback.answer(
            "Access denied.",
            show_alert=True,
        )
        return

    await state.set_state(
        AdminStates.waiting_broadcast
    )

    await callback.message.edit_text(
        "📢 <b>BROADCAST</b>\n\n"
        "Message type karo.",
        parse_mode="HTML",
    )

    await callback.answer()


@router.message(AdminStates.waiting_broadcast)
async def send_broadcast(
    message: Message,
    state: FSMContext,
    bot,
):

    success = 0
    failed = 0

    for user_id in list(users.keys()):

        try:

            await bot.send_message(
                user_id,
                "📢 <b>Announcement</b>\n\n"
                + message.text,
                parse_mode="HTML",
            )

            success += 1

        except Exception:

            failed += 1

    await message.answer(
        "📢 <b>Broadcast Finished</b>\n\n"
        f"Sent: {success}\n"
        f"Failed: {failed}",
        parse_mode="HTML",
    )

    await state.clear()


# ==========================================================
# ADMIN JOURNEYS
# ==========================================================

@router.callback_query(F.data == "admin_journeys")
async def admin_journeys(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):

        await callback.answer(
            "Access denied.",
            show_alert=True,
        )
        return

    if not journeys:

        text = "🚆 No journeys."

    else:

        text = "🚆 <b>JOURNEYS</b>\n\n"

        for user_id, journey in journeys.items():

            text += (
                f"User: <code>{user_id}</code>\n"
                f"{journey.get('source')} → "
                f"{journey.get('destination')}\n"
                f"Date: {journey.get('date')}\n"
                f"Train: {journey.get('train_number')}\n\n"
            )

    await callback.message.edit_text(
        text,
        reply_markup=admin_back(),
        parse_mode="HTML",
    )

    await callback.answer()


# ==========================================================
# ADMIN MONITORING
# ==========================================================

@router.callback_query(F.data == "admin_monitoring")
async def admin_monitoring(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):

        await callback.answer(
            "Access denied.",
            show_alert=True,
        )
        return

    active = sum(
        1
        for journey in journeys.values()
        if journey.get("alert")
    )

    await callback.message.edit_text(
        "🔎 <b>MONITORING</b>\n\n"
        f"Active monitoring jobs: {active}\n\n"
        "Dummy railway monitoring engine.",
        reply_markup=admin_back(),
        parse_mode="HTML",
    )

    await callback.answer()


# ==========================================================
# ADMIN LOGS
# ==========================================================

@router.callback_query(F.data == "admin_logs")
async def admin_logs(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):

        await callback.answer(
            "Access denied.",
            show_alert=True,
        )
        return

    if not logs:

        text = "📝 No logs."

    else:

        text = "📝 <b>RECENT LOGS</b>\n\n"

        for item in logs[-20:]:

            text += (
                f"• {item['event']}\n"
                f"User: {item['user_id']}\n\n"
            )

    await callback.message.edit_text(
        text,
        reply_markup=admin_back(),
        parse_mode="HTML",
    )

    await callback.answer()


# ==========================================================
# ADMIN SYSTEM
# ==========================================================

@router.callback_query(F.data == "admin_system")
async def admin_system(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):

        await callback.answer(
            "Access denied.",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        "🔄 <b>SYSTEM STATUS</b>\n\n"
        "Bot: 🟢 Online\n"
        "Database: 🟡 Temporary Memory\n"
        "Railway API: 🟡 Dummy\n"
        "Payment: 🟡 Demo\n"
        "Hosting: 🟢 Render",
        reply_markup=admin_back(),
        parse_mode="HTML",
    )

    await callback.answer()
