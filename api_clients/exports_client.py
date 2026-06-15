import time
from api_clients.base_client import BaseClient


class ExportsClient(BaseClient):
    def create_export(self, extension: str, **filters):
        payload = {"source": "transactions", "extension": extension, **filters}
        return self.post("/exports/", json=payload)

    def get_status(self, export_id: int):
        return self.get(f"/exports/{export_id}/")

    def download(self, export_id: int):
        return self.get(f"/exports/{export_id}/download/")

    def wait_until_done(self, export_id: int, timeout: int = 60, interval: int = 3):
        elapsed = 0
        while elapsed < timeout:
            response = self.get_status(export_id)
            status = response.json()["response"]["status"]
            if status == "DONE":
                return response
            if status == "FAILED":
                raise RuntimeError(f"Export {export_id} failed")
            # PENDING и RUNNING — ждём дальше
            time.sleep(interval)
            elapsed += interval
        raise TimeoutError(f"Export {export_id} not done in {timeout}s")
