from models import RideRequest, VALID_DESTINATIONS, VALID_TIME_SLOTS

class CabPoolApp:
    def __init__(self):
        self.cabs = []
        self.waiting_requests = []
        self.request_counter = 0

    def add_request(self):
        print("\n--- Add New Ride Request ---")
        name = input("Student Name: ").strip()
        if not name:
            print("Error: Name cannot be empty.")
            return

        destination = input(f"Destination ({'/'.join(VALID_DESTINATIONS)}): ").strip().capitalize()
        if destination not in VALID_DESTINATIONS:
            print(f"Error: Invalid destination. Must be one of {', '.join(VALID_DESTINATIONS)}.")
            return

        time_slot = input(f"Time Slot ({'/'.join(VALID_TIME_SLOTS)}): ").strip().capitalize()
        if time_slot not in VALID_TIME_SLOTS:
            print(f"Error: Invalid time slot. Must be one of {', '.join(VALID_TIME_SLOTS)}.")
            return

        try:
            year = int(input("Year of Study (1-5): ").strip())
            if not (1 <= year <= 5):
                raise ValueError()
        except ValueError:
            print("Error: Year must be an integer between 1 and 5.")
            return

        self.request_counter += 1
        request = RideRequest(name, destination, time_slot, year, self.request_counter)
        self.waiting_requests.append(request)
        print("Success! Request added to waiting list.")

    def show_status(self):
        print("\n WAITING LIST & CABS ")
        print(f"Waiting requests count: {len(self.waiting_requests)}")
        for req in self.waiting_requests:
            print(f" - {req.name} going to {req.destination} ({req.time_slot}), Year {req.year}")

    def menu(self):
        while True:
            print("\n1. Add a new ride request")
            print("2. See everyone still waiting")
            print("3. Quit")
            choice = input("Enter choice (1-3): ").strip()

            if choice == "1":
                self.add_request()
            elif choice == "2":
                self.show_status()
            elif choice == "3":
                print("Exiting...")
                break
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    CabPoolApp().menu()