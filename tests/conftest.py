"""Fixtures for the tests."""

import json
from collections.abc import Generator
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from httpx import Response
from http import HTTPMethod

from lmcloud.client_cloud import LaMarzoccoCloudClient
from lmcloud.lm_machine import LaMarzoccoMachine


def load_fixture(device_type: str, file_name: str) -> dict:
    """Load a fixture."""
    with open(
        f"{Path(__file__).parent}/fixtures/{device_type}/{file_name}", encoding="utf-8"
    ) as f:
        return json.load(f)


def get_mock_response(*args, **kwargs) -> Response:
    """Get a mock response from HTTP request."""
    method: HTTPMethod = args[0]
    url: str = str(args[1])

    device_type = "machine"
    data: dict = {"data": {"commandId": "123456"}}
    if "configuration" in url:
        data = load_fixture(device_type, "config.json")
    elif "firmware" in url:
        data = load_fixture(device_type, "firmware.json")
    elif "counters" in url:
        data = load_fixture(device_type, "counters.json")
    elif "/commands/" in url:
        data["data"] = {"status": "COMPLETED", "responsePayload": {"status": "success"}}

    if method == HTTPMethod.GET:
        return Response(200, json=data)
    return Response(204, json=data)


@pytest.fixture
def cloud_client() -> Generator[LaMarzoccoCloudClient, None, None]:
    """Fixture for a cloud client."""

    client = LaMarzoccoCloudClient("username", "password")

    oauth_client = AsyncMock()
    oauth_client.request.side_effect = get_mock_response

    client._oauth_client = oauth_client  # pylint: disable=protected-access
    yield client
