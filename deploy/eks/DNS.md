# DNS Plan

Целевой production hostname: `prizma.pernyaev.ru`

## Cloudflare zone: `pernyaev.ru`

Так как `pernyaev.ru` уже делегирован на Cloudflare (`meilani.ns.cloudflare.com`, `roman.ns.cloudflare.com`), production-запись нужно создавать именно там.

### Вариант 1: ingress с публичным IP

Создать запись:

- `A`
- `Name`: `prizma`
- `Content`: `95.163.244.138`, если именно этот публичный IP смотрит на ingress/load balancer
- `Proxy status`: `Proxied`, если нужен Cloudflare proxy и TLS на краю

### Вариант 2: AWS ALB / внешний load balancer hostname

Создать запись:

- `CNAME`
- `Name`: `prizma`
- `Target`: `<ALB_DNS_NAME>`
- `Proxy status`: `DNS only` или `Proxied` в зависимости от режима

Если используется `external-dns`, запись можно создавать автоматически из ingress-аннотации:

- `external-dns.alpha.kubernetes.io/hostname=prizma.pernyaev.ru`

## Reg.ru zone: `pernyaev.online`

Эту зону можно использовать для staging или редиректа.

Рекомендуемый вариант:

- `prizma.pernyaev.online` -> staging ingress
- `www.pernyaev.online` и `pernyaev.online` оставить как есть или редиректить отдельно

Если staging будет на том же ingress:

- `CNAME prizma -> <STAGING_LB_HOSTNAME>`

## Private network note

Приватный IP `192.168.0.165` из сети `private_network_119657669` не подходит для публичной DNS-записи. Внешний DNS должен указывать только на публичный ingress IP или LB hostname.

Cloudflare Tunnel нужен только если у сервера/кластера нет публичного входа на 80/443 или ты не хочешь открывать входящие порты. При наличии публичного ingress IP достаточно DNS-записи.
