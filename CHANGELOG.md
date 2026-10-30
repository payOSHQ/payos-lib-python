# Changelog

## 1.1.1 (2026-10-30)

### Bug Fixes

- **webhooks:** stricter webhook data validation; wire payloads that fail it now raise `WebhookError("Invalid webhook data: ...")` instead of `Webhook schema validation failed`
- **client:** response signature verification now fails closed and raises `InvalidSignatureError("Missing response signature")` when the signature is absent
- **core:** compare signatures in constant time
- **webhooks:** unknown wire webhook fields are now accepted and authenticated; they are omitted from the returned typed model (previously rejected by `extra="forbid"`)

## 1.1.0 (2026-06-22)

### Features

- **client:** add legacy compatibility layer to support v0.x code with deprecation warnings [#1](https://github.com/payOSHQ/payos-lib-python/issues/1)

## 1.0.1 (2026-01-05)

### Bug Fixes

- **core:** allow empty dict compute signature instead of return `None`
- **types:** change category field of `PayoutRequest` from `Optional[str]` to `Optional[list[str]]`
- **resources:** enhance async verify webhook to support multiple payload types

## 1.0.0 (2025-09-11)

Release v1. For full migrate guild see [MIGRATION.md](./MIGRATION.md).

### Features

- **api:** add `/v2/payment-request/invoices`
- **api:** add `/v1/payouts`
- **api:** add `/v1/payouts-account`
- **client:** add default value for credential read from environment variable
- **client:** add `crypto` to calculate signature for payment-requests and payouts signature
- **client:** add additional options to all method
- **client:** add logging
- **client:** add pagination support for get list request
- **client:** add retry for rate limit request
- **client:** add Error subclass to handle api error, webhook error and signature error for better error handling
- **client:** add support for request download file

### Documentation

- **readme:** update readme
