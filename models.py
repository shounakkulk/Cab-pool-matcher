VALID_DESTINATIONS = {"Delhi", "Jaipur"}
VALID_TIME_SLOTS = {"Morning", "Afternoon", "Evening", "Night"}

class RideRequest:
    def __init__(self, name: str, destination: str, time_slot: str, year: int, request_id: int):
        self.name = name
        self.destination = destination
        self.time_slot = time_slot
        self.year = year
        self.request_id = request_id

    def to_dict(self):
        return {
            "name": self.name,
            "destination": self.destination,
            "time_slot": self.time_slot,
            "year": self.year,
            "request_id": self.request_id
        }

class Cab:
    def __init__(self, driver: str, seats: int, destination: str, time_slot: str, has_left: bool = False, passengers: list = None):
        self.driver = driver
        self.seats = seats
        self.destination = destination
        self.time_slot = time_slot
        self.has_left = has_left
        if passengers is not None:
            self.passengers = passengers 
        else: 
            self.passengers = []

    def remaining_seats(self) -> int:
        return self.seats - len(self.passengers)

    def to_dict(self):
        return {
            "driver": self.driver,
            "seats": self.seats,
            "destination": self.destination,
            "time_slot": self.time_slot,
            "has_left": self.has_left,
            "passengers": self.passengers
        }