# Homelab

Kubernetes-managed self-hosted services running in a home lab environment. All resources are defined as plain Kubernetes manifests and deployed with `kubectl apply`.

## Services

| Service | Namespace | URL | Description |
|---------|-----------|-----|-------------|
| [Actual Budget](https://actualbudget.org) | `actual-budget` | `actual.lab` | Personal finance & budgeting |
| [AdGuard Home](https://adguard.com/adguard-home.html) | — | — | DNS-level ad-blocking (Docker Compose, not in cluster) |
| [code-server](https://github.com/coder/code-server) | `development` | `code.lab` | VS Code in the browser |
| [ERPNext](https://erpnext.com) | `erpnext` | `janak.medical` | ERP (Frappe, MariaDB, Redis) |
| [Excalidraw](https://excalidraw.com) | `excalidraw` | `draw.lab` | Whiteboard / diagram sketching |
| [Homepage](https://gethomepage.dev) | `homepage` | `home.lab` | Unified dashboard for all services |
| [Jellyfin](https://jellyfin.org) | `jellyfin` | `jellyfin.lab` | Media streaming server |
| [MinIO](https://min.io) | `minio` | `minio.lab` | S3-compatible object storage |
| [MySpeed](https://github.com/gnmyt/myspeed) | `myspeed` | `myspeed.lab` | Internet speed test tracking |
| [n8n](https://n8n.io) | `n8n` | `n8n.lab` | Workflow automation |
| [Paperless-ngx](https://docs.paperless-ngx.com) | `paperless` | `paperless.lab` | Document management |
| [qBittorrent](https://www.qbittorrent.org) | `qbittorrent` | `torrent.lab` | Torrent client |
| [Qdrant](https://qdrant.tech) | `qdrant` | `qdrant.lab` | Vector database for AI/embeddings |
| Security camera | `camera` | `camera.lab` | HLS camera stream + custom backend |
| [Vaultwarden](https://github.com/dani-garcia/vaultwarden) | `vaultwarden` | `passwords.lab` | Bitwarden-compatible password manager |
| [Loki](https://grafana.com/oss/loki/) + [Alloy](https://grafana.com/oss/alloy/) | `logging` | — | Log aggregation and collection |

### Infrastructure

| Service | Namespace | URL | Description |
|---------|-----------|-----|-------------|
| PostgreSQL + Adminer | `postgres` | `adminer.lab` | Shared database for workloads |
| MongoDB + Mongo Express | `mongodb` | `mongo.lab` | Document store (chatbot conversations) |
| Redis + RedisInsight | `redis` | `redis.lab` | Shared cache / key-value store |
| PlantUML | `infrastructure` | `plantuml.lab` | Diagram-as-code rendering |
| Grafana | `monitoring` | `grafana.lab` | Metrics dashboards (ingress only) |

## Layout

```
├── apps/                  # Application deployments
│   ├── actual-budget/
│   ├── adguard/           # Docker Compose (outside cluster)
│   ├── code-server/
│   ├── erpnext/
│   ├── excalidraw/
│   ├── homepage/
│   ├── jellyfin/
│   ├── logging/           # loki/ and alloy/ subdirectories
│   ├── minIO/
│   ├── mySpeed/
│   ├── n8n/
│   ├── paperless/
│   ├── qbittorrent/
│   ├── qdrant/
│   ├── security-camera/   # includes a custom backend/ image
│   └── vaultwarden/
└── infrastructure/        # Supporting infrastructure
    ├── mongodb/
    ├── monitoring/
    ├── plantuml/
    ├── postgres/
    └── redis/
```

## Usage

Apply a single service:

```sh
kubectl apply -f apps/jellyfin/
```

Apply everything (`-R` picks up nested directories such as `apps/logging/`):

```sh
kubectl apply -R -f apps/ -f infrastructure/
```

Delete a service:

```sh
kubectl delete -f apps/jellyfin/
```

> **Note:** `apps/adguard/` runs via Docker Compose (`docker compose up -d`) — it's not part of the Kubernetes cluster.

> **Note:** `kubectl apply -f <dir>/` applies files alphabetically, so on a first deploy the namespace may not exist yet when other resources are created. Re-run the apply if you see `namespaces "..." not found`.

## Secrets

Secrets live in `secret.yaml` / `secrets.yaml` files next to the manifests that use them. These are gitignored and must be created locally before applying a service.

Homepage widget credentials are kept in `apps/homepage/secret.yaml` (Secret `homepage-secret`) and referenced in `services.yaml` as `{{HOMEPAGE_VAR_<NAME>}}`. Expected keys:

- `HOMEPAGE_VAR_JELLYFIN_KEY`
- `HOMEPAGE_VAR_QBITTORRENT_PASSWORD`
- `HOMEPAGE_VAR_ADGUARD_PASSWORD`
- `HOMEPAGE_VAR_MYSPEED_PASSWORD`

## Domains

Most services are exposed via Kubernetes Ingress. The lab uses an internal domain `*.lab` — point your DNS or `/etc/hosts` accordingly.

You can find service URLs in `apps/homepage/config/services.yaml`.
