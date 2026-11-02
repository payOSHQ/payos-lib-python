# Changelog

## 1.1.1 (2026-10-30)

### Bug Fixes

- **webhooks:** stricter webhook data validation; wire payloads that fail it now raise `WebhookError("Invalid webhook data: ...")` instead of `Webhook schema validation failed` ([GHSA-7w9h-f6cc-xjmw](https://github.com/payOSHQ/payos-lib-python/security/advisories/GHSA-7w9h-f6cc-xjmw))
- **client:** response signature verification now fails closed and raises `InvalidSignatureError("Missing response signature")` when the signature is absent ([GHSA-7884-9wf9-7vgm](https://github.com/payOSHQ/payos-lib-python/security/advisories/GHSA-7884-9wf9-7vgm))
- **core:** compare signatures in constant time
- **webhooks:** unknown wire webhook fields are now accepted and authenticated; they are omitted from the returned typed model (previously rejected by `extra="forbid"`)
- **client:** percent-encode identifiers interpolated into API paths (including the legacy `getPaymentLinkInformation`/`cancelPaymentLink`) and reject empty, `.`/`..`, negative or unsafe-integer values; when a custom `http_client` follows redirects, follow only 301/302/303/307/308 (max 5 redirects) and, once the chain leaves the original origin, stop sending `x-api-key`/`x-client-id`/`x-partner-code`/`authorization`/`cookie`/`proxy-authorization` and client auth for the rest of the chain; validate body-signed response data (`&key=` sequences, unsupported keys, nested objects, non-finite or unsafe numbers) before verifying its signature, raising `InvalidSignatureError`

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
