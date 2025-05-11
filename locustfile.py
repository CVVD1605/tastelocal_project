from locust import HttpUser, task, between

class BookingUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://127.0.0.1:8000"

    @task
    def access_booking_page(self):
        self.client.get("/vendor/booking/1/") 
