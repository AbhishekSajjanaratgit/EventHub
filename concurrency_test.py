"""
Concurrency test for EventHub.

Creates an event with 10 seats, then fires 30 booking requests (1 seat each) at the exact
same moment. If the reservation logic is race-safe, exactly 10 bookings succeed (201) and
the other 20 are rejected (400), leaving 0 seats and 10 confirmed reservations.

Useage : Django server must already be running in another terminal.
    command : python concurrency_test.py
"""

import threading
from collections import Counter

import requests

BASE_URL = 'http://127.0.0.1:8000/api'
TOTAL_SEATS = 10
NUM_REQUESTS = 30
SEATS_PER_BOOKING = 1

def main():
    # 1. Create a fresh event for this test run
    resp = requests.post(f'{BASE_URL}/events/',json={
        'title': 'Concurrency Test Event',
        'venue': 'Test Hall',
        'date': '2026-12-01',
        'total_seats': TOTAL_SEATS,
        'available_seats': TOTAL_SEATS,
        'status': 'upcoming',
    })

    resp.raise_for_status()
    event = resp.json()

    print(f"Created event id={event['id']} with {TOTAL_SEATS} seats")
    print(f"Firing {NUM_REQUESTS} booking requests at the same time...\n")

    results = []
    results_lock = threading.Lock()
    start_line = threading.Barrier(NUM_REQUESTS)


    def book(i):
        start_line.wait()
        r = requests.post(f'{BASE_URL}/reservations/', json={
            'event': event['id'],
            'attendee_name': f'User {i}',
            'attendee_email': f'user{i}@example.com',
            'seats_reserved': SEATS_PER_BOOKING,
        })

        with results_lock:
            results.append(r.status_code)

    # 2. Start all threads, then wait for all the threads to finish

    threads = [threading.Thread(target=book, args=(i,)) for i in range(NUM_REQUESTS)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    # 3. Check the final status of the event

    final = requests.get(f"{BASE_URL}/events/{event['id']}/").json()
    counts = Counter(results)

    expected_success = TOTAL_SEATS // SEATS_PER_BOOKING
    expected_rejected = NUM_REQUESTS - expected_success

    print(f"Status codes      : {dict(counts)}")
    print(f"Expected          : {{201: {expected_success}, 400: {expected_rejected}}}")
    print(f"Seats left        : {final['available_seats']} (expected 0)")
    print(f"Confirmed bookings: {final['reservations_count']} (expected {expected_success})")

    passed = (
        counts.get(201, 0) == expected_success
        and counts.get(400, 0) == expected_rejected
        and final['available_seats'] == 0
        and final['reservations_count'] == expected_success
    )

    print('\nRESULT:', 'PASS - no overselling' if passed else 'FAIL - check the reservation logic')


if __name__ == "__main__":
    main()