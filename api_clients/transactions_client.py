from api_clients.base_client import BaseClient
from utils.config import API_V1_URL, API_V4_URL


class TransactionsClient(BaseClient):
    def __init__(self, token: str = None):
        super().__init__(token=token, base_url=API_V4_URL)
        self._v1_url = API_V1_URL

    def get_transactions(
        self,
        created_range: str = None,
        payed_range: str = None,
        type_in: str = None,
        payment_method: str = None,
        page: int = 1,
        size: int = 10,
    ):
        params = {"page": page, "size": size}
        if created_range:
            params["created__range"] = created_range
        if payed_range:
            params["payed__range"] = payed_range
        if type_in:
            params["type__in"] = type_in
        if payment_method:
            params["payment_method"] = payment_method
        return self.get("/transactions/", params=params)

    def get_filter_partners(self):
        return self.session.get(f"{self._v1_url}/transactions/filters/partners/")

    def get_filter_services(self):
        return self.session.get(f"{self._v1_url}/transactions/filters/services/")

    def get_filter_statuses(self):
        return self.session.get(f"{self._v1_url}/transactions/filters/statuses/")

    def refund(self, transaction_id: int, cost: str, refund_receipt_data: str = None):
        payload = {"cost": cost}
        if refund_receipt_data:
            payload["refund_receipt_data"] = refund_receipt_data
        return self.session.post(
            f"{self._v1_url}/transactions/{transaction_id}/refund/",
            json=payload,
        )

    def send_webhook(self, transaction_id: int):
        return self.session.post(
            f"{self._v1_url}/transactions/{transaction_id}/send-webhook/",
            json={},
        )

    def request_status(self, transaction_id: int):
        return self.session.post(
            f"{self._v1_url}/transactions/{transaction_id}/status/",
            json={},
        )
