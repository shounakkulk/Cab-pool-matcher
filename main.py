import json
import os
import heapq
from collections import defaultdict

VALID_DESTINATIONS = {"Delhi", "Jaipur"}
VALID_TIME_SLOTS = {"Morning", "Afternoon", "Evening", "Night"}
STATE_FILE = "app_state.json"
CABS_FILE = "cabs.json"

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

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            destination=data["destination"],
            time_slot=data["time_slot"],
            year=data["year"],
            request_id=data["request_id"]
        )


class PriorityRideQueue:
    def __init__(self):
        self._heap = []

    def push(self, request: RideRequest):
        heap_item = (-request.year, request.request_id, request)
        heapq.heappush(self._heap, heap_item)

    def pop(self) -> RideRequest:
        if self.is_empty():
            raise IndexError("Pop from empty queue")
        _, _, request = heapq.heappop(self._heap)
        return request

    def peek_n(self, n: int) -> list[RideRequest]:
        sorted_elements = sorted(self._heap)
        result = []
        count = 0
        for item in sorted_elements:
            if count >= n:
                break
            request_obj = item[2]
            result.append(request_obj)
            count += 1
        return result

    def get_all(self) -> list[RideRequest]:
        sorted_elements = sorted(self._heap)
        result = []
        for item in sorted_elements:
            result.append(item[2])
        return result

    def is_empty(self) -> bool:
        if len(self._heap) == 0:
            return True
        return False

    def __len__(self) -> int:
        return len(self._heap)


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

    @property
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

    @classmethod
    def from_dict(cls, data):
        return cls(
            driver=data["driver"],
            seats=data["seats"],
            destination=data["destination"],
            time_slot=data["time_slot"],
            has_left=data.get("has_left", False),
            passengers=data.get("passengers", [])
        )


class CabPoolApp:
    def __init__(self):
        self.cabs = []
        self.queues = defaultdict(PriorityRideQueue)
        self.request_counter = 0
        self.load_data()

    def get_trip_key(self, dest: str, slot: str) -> tuple[str, str]:
        return (dest.capitalize(), slot.capitalize())

    def load_data(self):
        if os.path.exists(STATE_FILE):
            try:
                file_handle = open(STATE_FILE, "r")
                state = json.load(file_handle)
                file_handle.close()
                
                self.request_counter = state.get("request_counter", 0)
                
                self.cabs = []
                for cab_dict in state.get("cabs", []):
                    self.cabs.append(Cab.from_dict(cab_dict))
                
                for req_dict in state.get("waiting_requests", []):
                    req = RideRequest.from_dict(req_dict)
                    key = self.get_trip_key(req.destination, req.time_slot)
                    self.queues[key].push(req)
                    
                print("Loaded previous session state from app_state.json successfully.")
                return
            except Exception as e:
                print(f"Warning: Failed to parse {STATE_FILE} ({e}). Starting fresh.")

        if os.path.exists(CABS_FILE):
            try:
                file_handle = open(CABS_FILE, "r")
                data = json.load(file_handle)
                file_handle.close()
                
                self.cabs = []
                for cab_dict in data:
                    self.cabs.append(Cab.from_dict(cab_dict))
                print("Loaded initial cabs from cabs.json successfully.")
            except Exception as e:
                print(f"Error loading {CABS_FILE}: {e}")
        else:
            print("Warning: Neither state file nor cabs.json found. Starting with zero cabs.")

    def save_data(self):
        waiting_requests = []
        for queue in self.queues.values():
            for req in queue.get_all():
                waiting_requests.append(req.to_dict())

        state = {
            "request_counter": self.request_counter,
            "cabs": [cab.to_dict() for cab in self.cabs],
            "waiting_requests": waiting_requests
        }

        try:
            file_handle = open(STATE_FILE, "w")
            json.dump(state, file_handle, indent=2)
            file_handle.close()
        except Exception as e:
            print(f"Failed to save state: {e}")

    def add_request(self):
        print("\n--- Add New Ride Request ---")
        name = input("Student Name: ").strip()
        if not name:
            print("Error: Name cannot be empty.")
            return

        destination = input(f"Destination ({'/'.join(VALID_DESTINATIONS)}): ").strip().capitalize()
        if destination not in VALID_DESTINATIONS:
            print(f"Error: Invalid destination. We only serve {', '.join(VALID_DESTINATIONS)}.")
            return

        time_slot = input(f"Time Slot ({'/'.join(VALID_TIME_SLOTS)}): ").strip().capitalize()
        if time_slot not in VALID_TIME_SLOTS:
            print(f"Error: Invalid time slot. Must be one of {', '.join(VALID_TIME_SLOTS)}.")
            return

        try:
            year_input = input("Year of Study (1-5): ").strip()
            year = int(year_input)
            if year < 1 or year > 5:
                print("Error: Year must be between 1 and 5.")
                return
        except ValueError:
            print("Error: Year must be a valid integer.")
            return

        self.request_counter += 1
        request = RideRequest(
            name=name,
            destination=destination,
            time_slot=time_slot,
            year=year,
            request_id=self.request_counter
        )
        
        key = self.get_trip_key(destination, time_slot)
        self.queues[key].push(request)
        
        self.save_data()
        print(f"Success! Request added to waiting list for {destination} ({time_slot}).")

    def show_status(self):
        print("\nCURRENT SYSTEM STATUS")
        
        print("\nWaiting Lists")
        has_waiting_students = False
        for key, queue in self.queues.items():
            if not queue.is_empty():
                has_waiting_students = True
                dest, slot = key
                print(f"Trip: {dest} - {slot} ({len(queue)} waiting)")
                for req in queue.get_all():
                    print(f"  - {req.name} | Year {req.year} [Request ID: {req.request_id}]")
        
        if not has_waiting_students:
            print("  No students currently waiting.")

        print("\nCabs Status")
        for idx, cab in enumerate(self.cabs, 1):
            if cab.has_left:
                status = "LEFT"
            else:
                status = "OPEN"
            
            passengers_str = ", ".join(cab.passengers) if cab.passengers else "None"
            print(f"  [{idx}] Driver: {cab.driver} | Route: {cab.destination} ({cab.time_slot}) | "
                  f"Seats: {len(cab.passengers)}/{cab.seats} | Status: {status} | Passengers: {passengers_str}")

    def find_matches(self):
        print("\nMATCH PREVIEW")
        
        open_cabs = []
        for cab in self.cabs:
            if not cab.has_left:
                open_cabs.append(cab)

        if len(open_cabs) == 0:
            print("No open cabs available.")
            return

        for cab in open_cabs:
            key = self.get_trip_key(cab.destination, cab.time_slot)
            queue = self.queues[key]
            
            preview_passengers = queue.peek_n(cab.remaining_seats)
            
            names = []
            for student in preview_passengers:
                names.append(f"{student.name} (Yr {student.year})")

            if len(names) > 0:
                names_display = ", ".join(names)
            else:
                names_display = "No matching students waiting"

            print(f"Cab: {cab.driver} [{cab.destination}, {cab.time_slot}] | Open Seats: {cab.remaining_seats} | Would take: {names_display}")

    def dispatch_cab(self):
        print("\n--- Dispatch a Cab ---")
        dest_input = input(f"Select Destination ({'/' .join(VALID_DESTINATIONS)}): ").strip().capitalize()
        slot_input = input(f"Select Time Slot ({'/' .join(VALID_TIME_SLOTS)}): ").strip().capitalize()

        key = self.get_trip_key(dest_input, slot_input)
        queue = self.queues[key]

        matching_cab = None
        for cab in self.cabs:
            if not cab.has_left:
                if cab.destination == dest_input:
                    if cab.time_slot == slot_input:
                        matching_cab = cab
                        break

        if matching_cab is None:
            print(f"Error: No open cab available for trip {dest_input} - {slot_input}.")
            return

        if queue.is_empty():
            print(f"Notice: No students waiting for {dest_input} - {slot_input}. Cab cannot be dispatched.")
            return

        seats_to_fill = matching_cab.remaining_seats
        boarded_students = []
        
        while not queue.is_empty():
            if len(boarded_students) >= seats_to_fill:
                break
            student = queue.pop()
            boarded_students.append(student)

        for student in boarded_students:
            matching_cab.passengers.append(student.name)

        matching_cab.has_left = True
        
        self.save_data()

        boarded_names = []
        for student in boarded_students:
            boarded_names.append(f"{student.name} (Yr {student.year})")

        print(f"Success! Cab driven by {matching_cab.driver} has left for {dest_input} ({slot_input}) with passengers: {', '.join(boarded_names)}.")

    def menu(self):
        while True:
            print("\nMenu\n")
            print("1. Add a new ride request")
            print("2. See status")
            print("3. Find Matches")
            print("4. Dispatch a Cab")
            print("5. Quit")
            choice = input("Enter choice (1-5): ").strip()

            if choice == "1":
                self.add_request()
            elif choice == "2":
                self.show_status()
            elif choice == "3":
                self.find_matches()
            elif choice == "4":
                self.dispatch_cab()
            elif choice == "5":
                self.save_data()
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    app = CabPoolApp()
    app.menu()