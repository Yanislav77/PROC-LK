import csv
import io
import pytest
from api_clients.exports_client import ExportsClient
from api_clients.base_client import BaseClient

DATE_RANGE = "2026-06-08T00:00:00.000,2026-06-15T23:59:59.999"
EXPECTED_COLUMNS = {"Terminal ID", "Terminal name"}
REMOVED_COLUMNS = {"Service ID", "Service name"}


def make_client(auth_client) -> ExportsClient:
    token = auth_client.session.headers.get("Authorization", "").removeprefix("Bearer ")
    return ExportsClient(token=token)


@pytest.mark.api
@pytest.mark.smoke
class TestExportsCreate:
    @pytest.fixture(autouse=True)
    def setup(self, auth_client):
        self.client = make_client(auth_client)

    def test_create_csv_export(self):
        response = self.client.create_export(
            extension="csv",
            created__range=DATE_RANGE,
            type__in="payment",
        )
        assert response.status_code in (200, 201)
        assert response.json()["message"] == "success"
        data = BaseClient.unwrap(response)
        assert "id" in data
        assert data["status"] in ("PENDING", "RUNNING", "DONE")

    def test_create_xlsx_export(self):
        response = self.client.create_export(
            extension="xlsx",
            created__range=DATE_RANGE,
        )
        assert response.status_code in (200, 201)
        data = BaseClient.unwrap(response)
        assert "id" in data
        assert data["status"] in ("PENDING", "RUNNING", "DONE")

    def test_create_export_missing_extension(self):
        response = self.client.post("/exports/", json={"source": "transactions"})
        assert response.status_code == 400


@pytest.mark.api
class TestExportsStatus:
    @pytest.fixture(autouse=True)
    def setup(self, auth_client):
        self.client = make_client(auth_client)
        response = self.client.create_export(
            extension="csv", created__range=DATE_RANGE
        )
        self.export_id = BaseClient.unwrap(response)["id"]

    def test_get_export_status_returns_200(self):
        response = self.client.get_status(self.export_id)
        assert response.status_code == 200
        assert response.json()["message"] == "success"

    def test_get_export_status_valid_state(self):
        response = self.client.get_status(self.export_id)
        data = BaseClient.unwrap(response)
        assert data["status"] in ("PENDING", "RUNNING", "DONE", "FAILED")

    def test_get_export_status_fields(self):
        response = self.client.get_status(self.export_id)
        data = BaseClient.unwrap(response)
        for field in ("id", "created", "status", "extension", "filename"):
            assert field in data

    def test_get_export_status_id_matches(self):
        response = self.client.get_status(self.export_id)
        data = BaseClient.unwrap(response)
        assert data["id"] == self.export_id


@pytest.mark.api
class TestExportsDownload:
    @pytest.fixture(autouse=True)
    def setup(self, auth_client):
        self.client = make_client(auth_client)

    def _create_and_wait(self, extension: str):
        response = self.client.create_export(
            extension=extension, created__range=DATE_RANGE
        )
        export_id = BaseClient.unwrap(response)["id"]
        self.client.wait_until_done(export_id, timeout=60)
        return export_id

    def test_download_returns_200(self):
        export_id = self._create_and_wait("csv")
        response = self.client.download(export_id)
        assert response.status_code == 200

    def test_download_has_content_disposition(self):
        export_id = self._create_and_wait("csv")
        response = self.client.download(export_id)
        assert "Content-Disposition" in response.headers

    def test_csv_columns_terminal_id_and_name_present(self):
        export_id = self._create_and_wait("csv")
        response = self.client.download(export_id)
        content = response.content.decode("utf-8-sig")
        reader = csv.reader(io.StringIO(content))
        headers = next(reader)
        assert "Terminal ID" in headers, f"'Terminal ID' not found in {headers}"
        assert "Terminal name" in headers, f"'Terminal name' not found in {headers}"

    def test_csv_columns_service_id_and_name_absent(self):
        export_id = self._create_and_wait("csv")
        response = self.client.download(export_id)
        content = response.content.decode("utf-8-sig")
        reader = csv.reader(io.StringIO(content))
        headers = next(reader)
        assert "Service ID" not in headers, "'Service ID' должен быть переименован в 'Terminal ID'"
        assert "Service name" not in headers, "'Service name' должен быть переименован в 'Terminal name'"

    def test_xlsx_columns_terminal_id_and_name_present(self):
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not installed")
        export_id = self._create_and_wait("xlsx")
        response = self.client.download(export_id)
        wb = openpyxl.load_workbook(io.BytesIO(response.content))
        ws = wb.active
        headers = [cell.value for cell in ws[1]]
        assert "Terminal ID" in headers, f"'Terminal ID' not found in {headers}"
        assert "Terminal name" in headers, f"'Terminal name' not found in {headers}"
