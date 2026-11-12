import json
import pathlib

import pytest
from pydantic import ValidationError

from payos import AsyncPayOS, PayOS
from payos._core.exceptions import WebhookError
from payos.types.webhooks import Webhook

_VECTORS = json.loads(pathlib.Path(__file__).with_name("webhook-vectors.json").read_text("utf-8"))
CASES = _VECTORS["cases"]
TYPED_CASES = [c for c in CASES if c.get("typed")]
SIGNATURE_ONLY_REJECTS = ("R14", "R15")


def _ids(cases):
    return [c["id"] for c in cases]


def _sync_client():
    return PayOS(client_id="c", api_key="a", checksum_key=_VECTORS["checksumKey"])


def _async_client():
    return AsyncPayOS(client_id="c", api_key="a", checksum_key=_VECTORS["checksumKey"])


def _expected_order_code(case):
    return json.loads(case["body"])["data"]["orderCode"]


def _assert_wire_reject(case, exc):
    if not case["id"].startswith(SIGNATURE_ONLY_REJECTS):
        assert str(exc).startswith("Invalid webhook data")


@pytest.mark.parametrize("case", CASES, ids=_ids(CASES))
def test_sync_wire(case):
    client = _sync_client()
    if case["expect"] == "accept":
        assert client.webhooks.verify(case["body"]).order_code == _expected_order_code(case)
    else:
        with pytest.raises(WebhookError) as exc:
            client.webhooks.verify(case["body"])
        _assert_wire_reject(case, exc.value)


@pytest.mark.parametrize("case", CASES, ids=_ids(CASES))
async def test_async_wire(case):
    client = _async_client()
    if case["expect"] == "accept":
        result = await client.webhooks.verify(case["body"])
        assert result.order_code == _expected_order_code(case)
    else:
        with pytest.raises(WebhookError) as exc:
            await client.webhooks.verify(case["body"])
        _assert_wire_reject(case, exc.value)


def _build_model(case):
    try:
        return Webhook.model_validate(json.loads(case["body"]))
    except ValidationError:
        assert case["expect"] == "reject"
        return None


@pytest.mark.parametrize("case", TYPED_CASES, ids=_ids(TYPED_CASES))
def test_sync_typed(case):
    model = _build_model(case)
    if model is None:
        return
    client = _sync_client()
    if case["expect"] == "accept":
        assert client.webhooks.verify(model).order_code == _expected_order_code(case)
    else:
        with pytest.raises(WebhookError):
            client.webhooks.verify(model)


@pytest.mark.parametrize("case", TYPED_CASES, ids=_ids(TYPED_CASES))
async def test_async_typed(case):
    model = _build_model(case)
    if model is None:
        return
    client = _async_client()
    if case["expect"] == "accept":
        result = await client.webhooks.verify(model)
        assert result.order_code == _expected_order_code(case)
    else:
        with pytest.raises(WebhookError):
            await client.webhooks.verify(model)
