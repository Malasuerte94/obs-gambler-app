import requests

from utils.environment import is_dev


class APIClient:
    """A simple API client for handling GET, POST, and PATCH requests."""
    if is_dev():
        BASE_URL = "http://127.0.0.1:8000/api/"
    else:
        BASE_URL = "https://casinolabs.ro/api/"

    @classmethod
    def set_base_url(cls, url):
        """Update the base URL dynamically."""
        cls.BASE_URL = url


    @classmethod
    def get_url(cls, url, return_raw=False):
        """Send a GET request. If `return_raw=True`, return raw response content instead of JSON."""
        try:
            response = requests.get(f"{url}", stream=return_raw)  # Use stream for images
            response.raise_for_status()

            return response.content if return_raw else response.json()

        except requests.RequestException as e:
            print(f"GET Error: {e}")
            return None

    @classmethod
    def get(cls, endpoint, return_raw=False):
        """Send a GET request. If `return_raw=True`, return raw response content instead of JSON."""
        try:
            response = requests.get(f"{cls.BASE_URL}{endpoint}", stream=return_raw)  # Use stream for images
            response.raise_for_status()

            return response.content if return_raw else response.json()

        except requests.RequestException as e:
            print(f"GET Error: {e}")
            return None

    @classmethod
    def post(cls, endpoint, data=None, files=None):
        """Send a POST request with optional file upload."""
        try:
            response = requests.post(f"{cls.BASE_URL}{endpoint}", data=data, files=files)
            response.raise_for_status()
            return response.json() if response.content else {"error": "Empty response from server"}
        except requests.RequestException as e:
            print(f"POST Error: {e}")
            return {"error": str(e)}

    @classmethod
    def patch(cls, endpoint, data):
        """Send a PATCH request."""
        try:
            response = requests.patch(f"{cls.BASE_URL}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"PATCH Error: {e}")
            return None
