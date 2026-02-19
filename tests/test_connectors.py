from app.connectors.crm_connector import CRMConnector
from app.connectors.support_connector import SupportConnector
from app.connectors.analytics_connector import AnalyticsConnector


def test_crm_connector_loads_data():
    connector = CRMConnector()
    data = connector.fetch()

    assert isinstance(data, list)
    assert len(data) > 0
    assert "customer_id" in data[0]


def test_support_connector_status_filter():
    connector = SupportConnector()
    data = connector.fetch(status="open")

    for item in data:
        assert item["status"] == "open"


def test_support_connector_priority_filter():
    connector = SupportConnector()
    data = connector.fetch(priority="low")

    for item in data:
        assert item["priority"] == "low"


def test_analytics_connector_metric_filter():
    connector = AnalyticsConnector()
    data = connector.fetch(metric="daily_active_users")

    for item in data:
        assert item["metric"] == "daily_active_users"

