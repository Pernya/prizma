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

## Kubernetes

Install an nginx ingress controller and cert-manager in the cluster, then deploy:

```bash
kubectl apply -f deploy/regcloud/namespace.yaml
helm upgrade --install prizma charts/prizma \
  --namespace prizma \
  -f charts/prizma/values-regcloud.yaml
```

This profile keeps API and worker replicas at `1` because the current file-based job repository needs shared state. For horizontal scaling, switch `sharedState` to an RWX storage class or replace the job repository with a database-backed implementation.
