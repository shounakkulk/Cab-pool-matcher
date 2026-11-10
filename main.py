import json
import os
from models import Cab, RideRequest, VALID_DESTINATIONS, VALID_TIME_SLOTS

class CabPoolApp:
    def __init__(self):
        self.cabs = []
        self.waiting_requests = []
        self.request_counter = 0
        self.load_cabs()

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
        self.waiting_requests.append(request)
        print("Success! Request added to waiting list.")

    def show_status(self):
        print("\n=== CURRENT SYSTEM STATUS ===")
        print(f"Total students waiting: {len(self.waiting_requests)}")
        
        print("\nWaiting Requests:")
        if len(self.waiting_requests) == 0:
            print("  No students waiting.")
        else:
            for req in self.waiting_requests:
                print(f"  - {req.name} | Destination: {req.destination} | Slot: {req.time_slot} | Year: {req.year}")

        print("\nCabs Status:")
        for idx, cab in enumerate(self.cabs, 1):
            if cab.has_left:
                status = "LEFT"
            else:
                status = "OPEN"
            
            passengers_str = ", ".join(cab.passengers) if cab.passengers else "None"
            print(f"  [{idx}] Driver: {cab.driver} | {cab.destination} ({cab.time_slot}) | "
                  f"Seats Taken: {len(cab.passengers)}/{cab.seats} | Status: {status} | Passengers: {passengers_str}")

    def find_matches(self):
        print("\n=== MATCH PREVIEW (No changes made) ===")
        

        open_cabs = []
        for cab in self.cabs:
            if not cab.has_left:
                open_cabs.append(cab)

        if len(open_cabs) == 0:
            print("No open cabs available.")
            return

        for cab in open_cabs:

            matching = []
            for req in self.waiting_requests:
                if req.destination == cab.destination:
                    if req.time_slot == cab.time_slot:
                        matching.append(req)

            selected = matching[:cab.remaining_seats()]
            

            names = []
            for student in selected:
                names.append(student.name)

            if len(names) > 0:
                names_display = ", ".join(names)
            else:
                names_display = "None"

            print(f"Cab ({cab.driver}) [{cab.destination}, {cab.time_slot}] | Open Seats: {cab.remaining_seats()} | Would take: {names_display}")

    def dispatch_cab(self):
        print("\n Dispatch a Cab ")
        dest_input = input("Destination to dispatch: ").strip().capitalize()
        slot_input = input("Time slot to dispatch: ").strip().capitalize()

        matching_cab = None
        for cab in self.cabs:
            if not cab.has_left:
                if cab.destination == dest_input:
                    if cab.time_slot == slot_input:
                        matching_cab = cab
                        break

        if matching_cab is None:
            print("Error: No open cab found matching that destination and time slot.")
            return

        matching_students = []
        for req in self.waiting_requests:
            if req.destination == dest_input:
                if req.time_slot == slot_input:
                    matching_students.append(req)

        if len(matching_students) == 0:
            print("Error: No students are waiting for this trip.")
            return

        boarded_students = matching_students[:matching_cab.remaining_seats()]

        for student in boarded_students:
            matching_cab.passengers.append(student.name)
            self.waiting_requests.remove(student)

        matching_cab.has_left = True

        boarded_names = []
        for student in boarded_students:
            boarded_names.append(student.name)

        print(f"Cab driven by {matching_cab.driver} has successfully left for {dest_input} ({slot_input}) with passengers: {', '.join(boarded_names)}!")

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