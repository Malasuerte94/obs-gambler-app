import requests

class APIClient:
    def __init__(self, settings):
        self.BASE_URL = settings.get('api_url', '')

    def get_url(self, url, return_raw=False):
        try:
            response = requests.get(f"{url}", stream=return_raw)
            response.raise_for_status()

            return response.content if return_raw else response.json()

        except requests.RequestException as e:
            print(f"GET Error: {e}")
            return None

    def get(self, endpoint, return_raw=False):
        try:
            response = requests.get(f"{self.BASE_URL}{endpoint}", stream=return_raw)
            response.raise_for_status()

            return response.content if return_raw else response.json()

        except requests.RequestException as e:
            print(f"GET Error: {e}")
            return None

    def post(self, endpoint, data=None, files=None, json=None):
        try:
            if json:
                response = requests.post(f"{self.BASE_URL}{endpoint}", json=json, files=files)
            else:
                response = requests.post(f"{self.BASE_URL}{endpoint}", data=data, files=files)

            response.raise_for_status()
            return response.json() if response.content else {"error": "Empty response from server"}
        except requests.RequestException as e:
            print(f"POST Error: {e}")
            return {"error": str(e)}

    def patch(self, endpoint, data):
        try:
            response = requests.patch(f"{self.BASE_URL}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"PATCH Error: {e}")
            return None