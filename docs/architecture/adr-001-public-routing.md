# ADR-001: Public Routing For MVP Demo

## Decision

Use `prizma.pernyaev.ru` for the public static frontend on the Reg.ru server and
`api.pernyaev.ru` for Cloudflare Tunnel access to the backend running on the Mac.

## Rationale

- Keeps backend and heavy processing local as requested.
- Allows the frontend to be reachable from the public internet.
- Avoids wildcard TLS issues for multi-level hostnames such as `api.prizma.pernyaev.ru`.
- Keeps the path open for a later Kubernetes ingress migration.

## Consequences

- The Cloudflare Tunnel process must stay running while the Mac hosts the backend.
- Production Kubernetes should replace this split with ingress and managed TLS.
- Frontend uses relative `/api/...` paths through nginx, while backend returns proxy-aware URLs.
