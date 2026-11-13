# Cab Pool Matcher (SUTT Task 1)

A CLI app written in Python to help coordinate campus cab sharing for end-of-sem travel to Delhi or Jaipur. It manages requests, pairs students up by trip timings, and prioritizes senior batches when seats fill up.

## Prerequisites

1. Make sure you're running Python 3.8+.

2. Make sure `cabs.json` is present in the root directory.

3. Run the application:

   ```
   python main.py
   
   ```

## Configuration & Data Files

The app reads initial cab data from `cabs.json`. It expects an array of cab objects looking like this:

```
[
  {
    "driver": "Ramesh",
    "seats": 4,
    "destination": "Delhi",
    "time_slot": "Morning",
    "has_left": false,
    "passengers": []
  },
  {
    "driver": "Suresh",
    "seats": 3,
    "destination": "Delhi",
    "time_slot": "Morning",
    "has_left": false,
    "passengers": []
  }
]

```

### Persistence Choice

I used JSON (`app_state.json`) for saving state between runs instead of `pickle`. JSON is human-readable, easier to inspect while testing/debugging, and doesn't run arbitrary Python code risks like `pickle` does.

Whenever you add a request, dispatch a cab, or quit the app, it creates/updates app_state.json with a snapshot of everything so you don't lose progress even if you hit Ctrl+C. It keeps track of three things:

request_counter: so new requests keep getting unique IDs after a restart.

cabs: the updated list of cabs, including who is inside and whether has_left is true or false.

waiting_requests: everyone still in the queues, saved with their original request_id so people in the same year keep their exact spot in line.

Here is what app_state.json looks like after a few actions:

```
{
  "request_counter": 3,
  "cabs": [
    {
      "driver": "Ramesh",
      "seats": 4,
      "destination": "Delhi",
      "time_slot": "Morning",
      "has_left": true,
      "passengers": ["Aarav", "Rohan"]
    }
  ],
  "waiting_requests": [
    {
      "name": "Kabir",
      "destination": "Jaipur",
      "time_slot": "Evening",
      "year": 2,
      "request_id": 3
    }
  ]
}

```
If app_state.json is missing or gets corrupted, the app just falls back to cabs.json and starts fresh.

## Technical Notes & Edge Cases

### 1. Half-empty cabs

If a cab is sent off with fewer passengers than its max seat limit, it takes whoever is currently available in the queue and sets `has_left = True`. Once dispatched, no more passengers can be added to it later.

### 2. No cabs available for a trip

If a student requests a ride for a trip with no open cabs (or if all cabs for that route have already left), their request stays safe in the queue. They show up under the status menu, and the app throws a friendly warning if someone tries to dispatch a cab for that slot without an open cab ready.

### 3. Seniority Priority & Tie-Breaking

* **Seniority:** Requests are stored in a min-heap using Python's `heapq`. The year is inverted (`-year`) so 5th years (-5) come out before 1st years (-1).

* **Same Year Tie-Breaking:** To ensure FIFO order for students in the same batch, each request gets an incrementing `request_id`. When two requests have the same year, `heapq` compares the `request_id`, so whoever signed up earlier gets picked first.

## Big-O Analysis

* **Adding 1 request:** O(log N) — Standard heap insertion time where N is the number of waiting requests for that specific trip.

* **Adding 1,000 requests:** O(K log K) — Performing K = 1,000 push operations into the trip priority queue.

* **Dispatching 1 cab:** O(C log N) — We pop up to C passengers (C <= 4) from the heap. Since max seats C is small and constant, it runs in O(log N) time.

* **Finding an open cab:** O(M) — A simple linear search over the array of M total cabs to find the first matching open cab.
