# Reg.Cloud Deployment Notes

Target hostname: `prizma.pernyaev.ru`

Known network context:

- Private network: `private_network_119657669`
- Subnet: `subnet_119657669`
- Private IP: `192.168.0.165`
- Public IP currently used by `pernyaev.online`: `95.163.244.138`

## DNS

`pernyaev.ru` is delegated to Cloudflare:

- `meilani.ns.cloudflare.com`
- `roman.ns.cloudflare.com`

If the Reg.Cloud ingress controller is exposed on `95.163.244.138`, create this Cloudflare DNS record:

- Type: `A`
- Name: `prizma`
- Content: `95.163.244.138`
- Proxy status: `Proxied` after HTTPS works, or `DNS only` while debugging certificates

The private IP `192.168.0.165` must not be used in public DNS. It is only for internal cluster or private-network traffic.

## Plain server mode

If `95.163.244.138` is a regular public server, not a Kubernetes ingress IP, run the public Docker Compose profile on that server:

```bash
docker compose -f docker-compose.server.yml -p prizma up -d --build
```

Only port `80` is published. nginx serves the static frontend from `web/` and proxies API traffic to the private backend container.

Check from any machine:

```bash
curl -I http://prizma.pernyaev.ru/
curl -I http://prizma.pernyaev.ru/healthz
```

## Frontend on server, backend on Mac

If most compute and backend operations must stay on the Mac, the public server cannot reach the Mac directly through `localhost`. Use Cloudflare Tunnel from the Mac for the API, and keep the static frontend on the Reg.ru server.

Target layout:

- `prizma.pernyaev.ru` -> `95.163.244.138` -> nginx frontend on the public server
- `api.pernyaev.ru` -> Cloudflare Tunnel -> Mac `http://localhost:8000`
- frontend calls relative `/api/...`; public nginx proxies those requests to `https://api.pernyaev.ru`

On the Mac:

```bash
docker compose -p prizma up -d --build backend worker minio rabbitmq
```

Create a Cloudflare Tunnel public hostname:

- Hostname: `api.pernyaev.ru`
- Service: `http://localhost:8000`

If using `cloudflared` CLI on the Mac:

```bash
cloudflared tunnel login
cloudflared tunnel create prizma-api
cloudflared tunnel route dns prizma-api api.pernyaev.ru
```

Then create `~/.cloudflared/config.yml` using [deploy/cloudflare/prizma-api-tunnel.example.yml](../cloudflare/prizma-api-tunnel.example.yml), replacing `<TUNNEL_ID>` with the id printed by `cloudflared tunnel create`.

Run the tunnel:

```bash
cloudflared tunnel run prizma-api
```

On the public Reg.ru server, run only the frontend nginx:

```bash
docker compose -f docker-compose.frontend-server.yml -p prizma-frontend up -d
```

GitHub Actions can deploy this mode automatically through `.github/workflows/deploy-vps.yml`.
Configure GitHub Environment `vps` with `VPS_HOST`, `VPS_PORT`, `VPS_USER`, `VPS_SSH_KEY` and
`VPS_APP_DIR`, then run `Actions -> Deploy VPS Frontend`.

Check:

```bash
curl -I http://prizma.pernyaev.ru/
curl -I http://prizma.pernyaev.ru/healthz
curl -I https://api.pernyaev.ru/healthz
```

## Kubernetes

Install an nginx ingress controller and cert-manager in the cluster, then deploy:

```bash
kubectl apply -f deploy/regcloud/namespace.yaml
kubectl apply -f deploy/regcloud/prizma-secrets.example.yaml
helm upgrade --install prizma charts/prizma \
  --namespace prizma \
  -f charts/prizma/values-regcloud.yaml
```

Replace the placeholder values in `deploy/regcloud/prizma-secrets.example.yaml` before production.
Leave `api-key` empty for a public demo; set it only if the caller can send `X-API-Key`.

This profile keeps API and worker replicas at `1` because the current file-based job repository needs shared state. For horizontal scaling, switch `sharedState` to an RWX storage class or replace the job repository with a database-backed implementation.
