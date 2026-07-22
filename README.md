# Homelab

Kubernetes-managed self-hosted services running in a home lab environment. All resources are defined as plain Kubernetes manifests and deployed with `kubectl apply`.

## Services

| Service | Namespace | Description |
|---------|-----------|-------------|
| [Actual Budget](https://actualbudget.org) | `actual-budget` | Personal finance & budgeting |
| [AdGuard Home](https://adguard.com/adguard-home.html) | — | DNS-level ad-blocking (Docker Compose, not in cluster) |
| [Homepage](https://gethomepage.dev) | `homepage` | Unified dashboard for all services |
| [Jellyfin](https://jellyfin.org) | `jellyfin` | Media streaming server |
| [MinIO](https://min.io) | `minio` | S3-compatible object storage |
| [n8n](https://n8n.io) | `n8n` | Workflow automation |
| [Plex](https://plex.tv) | `plex` | Media streaming server |
| [Qdrant](https://qdrant.tech) | `qdrant` | Vector database for AI/embeddings |

### Infrastructure

| Service | Namespace | Description |
|---------|-----------|-------------|
| PostgreSQL | `postgres` | Shared database for workloads |
| PlantUML | `plantuml` | Diagram-as-code rendering |
| Grafana | `monitoring` | Metrics dashboards (ingress only) |

## Layout

```
├── apps/                  # Application deployments
│   ├── actual-budget/
│   ├── adguard/           # Docker Compose (outside cluster)
│   ├── homepage/
│   ├── jellyfin/
│   ├── minIO/
│   ├── n8n/
│   ├── plex/
│   └── qdrant/
└── infrastructure/        # Supporting infrastructure
    ├── monitoring/
    ├── plantuml/
    └── postgres/
```

## Usage

Apply a single service:

```sh
kubectl apply -f apps/jellyfin/
```

Apply everything:

```sh
kubectl apply -f apps/ -f infrastructure/
```

Delete a service:

```sh
kubectl delete -f apps/plex/
```

> **Note:** `apps/adguard/` runs via Docker Compose (`docker compose up -d`) — it's not part of the Kubernetes cluster.

## Domains

Most services are exposed via Kubernetes Ingress. The lab uses an internal domain `*.lab` — point your DNS or `/etc/hosts` accordingly.

You can find service URLs in `apps/homepage/config/services.yaml`.
