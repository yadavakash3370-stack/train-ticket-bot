DUMMY_TRAINS = [
    {
        "number": "12301",
        "name": "Demo Rajdhani Express",
        "from": "PRYJ",
        "to": "NDLS",
        "departure": "22:10",
        "arrival": "06:30",
        "duration": "08h 20m",
        "classes": ["1A", "2A", "3A"],
        "seats": 24,
        "fare": 1450,
    },
    {
        "number": "12801",
        "name": "Demo Purushottam Express",
        "from": "PRYJ",
        "to": "NDLS",
        "departure": "22:30",
        "arrival": "08:15",
        "duration": "09h 45m",
        "classes": ["1A", "2A", "3A", "SL"],
        "seats": 67,
        "fare": 890,
    },
    {
        "number": "12417",
        "name": "Demo Prayagraj Express",
        "from": "PRYJ",
        "to": "NDLS",
        "departure": "21:20",
        "arrival": "07:00",
        "duration": "09h 40m",
        "classes": ["2A", "3A", "SL"],
        "seats": 42,
        "fare": 1050,
    },
]


async def search_trains(source, destination, journey_date):
    source = source.upper()
    destination = destination.upper()

    return [
        train.copy()
        for train in DUMMY_TRAINS
        if train["from"] == source and train["to"] == destination
    ]


async def check_availability(
    train_number,
    journey_date,
    travel_class,
):
    for train in DUMMY_TRAINS:
        if train["number"] == train_number:

            if travel_class not in train["classes"]:
                return {
                    "status": "CLASS_NOT_AVAILABLE",
                    "seats": 0,
                }

            return {
                "train_number": train["number"],
                "train_name": train["name"],
                "date": journey_date,
                "class": travel_class,
                "status": "AVAILABLE",
                "seats": train["seats"],
                "fare": train["fare"],
            }

    return {
        "status": "NOT_FOUND",
        "seats": 0,
    }
