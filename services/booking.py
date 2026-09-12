import random
import string


def generate_pnr():
    return "".join(
        random.choices(
            string.digits,
            k=10,
        )
    )


def generate_transaction_id():
    return "TXN" + "".join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=12,
        )
    )


async def create_dummy_booking(user_id, journey):

    return {
        "success": True,
        "status": "CONFIRMED",
        "pnr": generate_pnr(),
        "transaction_id": generate_transaction_id(),
        "user_id": user_id,
        "train_number": journey["train_number"],
        "train_name": journey["train_name"],
        "source": journey["source"],
        "destination": journey["destination"],
        "date": journey["date"],
        "travel_class": journey["travel_class"],
        "passenger": journey["passenger"],
    }
