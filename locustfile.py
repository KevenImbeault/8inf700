from locust import HttpUser, task

class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        self.client.get("/")

    @task
    def create_item(self):
        self.client.post("/create", data={"name": "Locust", "description": "Load testing with Locust"})