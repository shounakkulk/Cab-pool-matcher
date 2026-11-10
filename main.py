import json
import os
import heapq
from collections import defaultdict
from models import Cab, RideRequest, VALID_DESTINATIONS, VALID_TIME_SLOTS

class PriorityRideQueue:
    """Trip-specific heap queue maintaining senior priority (5 to 1) and FIFO tie-breaking."""
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
        """Returns top n requests in priority order without removing them."""
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
        """Returns all requests sorted by priority."""
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


class CabPoolApp:
    def __init__(self):
        self.cabs = []
        self.queues = defaultdict(PriorityRideQueue)
        self.request_counter = 0
        self.load_cabs()

    def get_trip_key(self, dest: str, slot: str) -> tuple[str, str]:
        return (dest.capitalize(), slot.capitalize())

    def load_cabs(self):
        if os.path.exists("cabs.json"):
            file_handle = open("cabs.json", "r")
            data = json.load(file_handle)
            file_handle.close()
            
            self.cabs = []
            for cab_dict in data:
                new_cab = Cab(
                    driver=cab_dict["driver"],
                    seats=cab_dict["seats"],
                    destination=cab_dict["destination"],
                    time_slot=cab_dict["time_slot"],
                    has_left=cab_dict.get("has_left", False),
                    passengers=cab_dict.get("passengers", [])
                )
                self.cabs.append(new_cab)
            print("Loaded cabs from cabs.json successfully.")
        else:
            print("Warning: cabs.json not found. Starting with zero cabs.")

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
        print(f"Success! Request added to waiting list for {destination} ({time_slot}).")

    def show_status(self):
        print("\n=== CURRENT SYSTEM STATUS ===")
        
        print("\n--- Waiting Lists (Grouped by Trip & Sorted by Seniority) ---")
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

        print("\n--- Cabs Status ---")
        for idx, cab in enumerate(self.cabs, 1):
            if cab.has_left:
                status = "LEFT"
            else:
                status = "OPEN"
            
            passengers_str = ", ".join(cab.passengers) if cab.passengers else "None"
            print(f"  [{idx}] Driver: {cab.driver} | Route: {cab.destination} ({cab.time_slot}) | "
                  f"Seats: {len(cab.passengers)}/{cab.seats} | Status: {status} | Passengers: {passengers_str}")

    def find_matches(self):
        print("\n=== MATCH PREVIEW (By Seniority - No changes made) ===")
        
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
        dest_input = input("Select Destination ({}) : ".format('/'.join(VALID_DESTINATIONS))).strip().capitalize()
        slot_input = input("Select Time Slot ({}) : ".format('/'.join(VALID_TIME_SLOTS))).strip().capitalize()

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

        boarded_names = []
        for student in boarded_students:
            boarded_names.append(f"{student.name} (Yr {student.year})")

        print(f"Success! Cab driven by {matching_cab.driver} has left for {dest_input} ({slot_input}) with passengers: {', '.join(boarded_names)}.")

    def menu(self):
            while True:

                print("\nMENU\n")

                print("1. Add a new ride request")
                print("2. See status (Waiting list & Cabs)")
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
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    app = CabPoolApp()
    app.menu()