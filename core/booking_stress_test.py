import threading
import requests
import time

URL = "http://127.0.0.1:8000/test-api/book/1/"  # Use your CSRF-exempt test endpoint
TOTAL_USERS = 500
success_count = 0
fail_count = 0
response_times = []

def make_booking():
    global success_count, fail_count
    try:
        start = time.time()
        response = requests.post(URL, json={
            "booking_date": "2025-05-20",
            "booking_time": "18:00",
            "number_of_people": 2,
            "special_request": "Stress test booking"
        })
        duration = time.time() - start
        response_times.append(duration)

        if response.status_code == 200:
            success_count += 1
        else:
            fail_count += 1
    except Exception as e:
        fail_count += 1
        print(f"[ERROR] {e}")

threads = []

print(f"Simulating {TOTAL_USERS} concurrent bookings...")

start_time = time.time()

for _ in range(TOTAL_USERS):
    t = threading.Thread(target=make_booking)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

total_time = time.time() - start_time

print(f"\n--- PT001 Stress Test Results ---")
print(f"Total Requests: {TOTAL_USERS}")
print(f"Successful: {success_count}")
print(f"Failed: {fail_count}")
print(f"Total Test Duration: {total_time:.2f} seconds")
print(f"Average Response Time: {sum(response_times)/len(response_times):.2f} seconds")
