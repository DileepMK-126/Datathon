# Production deployment guide

## Container deployment

1. Copy `.env.example` to `.env` and replace every placeholder through the approved secret-management workflow.
2. Keep `SEED_DEMO_DATA=true` only for an isolated demonstration. Set it to `false` only after an approved ingestion pipeline has been validated.
3. Start the stack:

```powershell
docker compose --env-file .env up --build
```

The web application is served on port 8080, the API on port 8000, and the local stack uses PostGIS. The initial administrator is the account in `BOOTSTRAP_ADMIN_USERNAME` and `BOOTSTRAP_ADMIN_PASSWORD`.

## Kubernetes handoff

The files in `deploy/kubernetes` are hardened deployment templates. Replace `registry.example.gov/sentinel/*:1.1.0` with signed images, apply the namespace and secret only through the cluster's secret manager integration, and use a managed PostGIS service with TLS. Do not apply `secret.example.yaml` unchanged.

```bash
kubectl apply -f deploy/kubernetes/namespace.yaml
kubectl apply -f deploy/kubernetes/api.yaml
kubectl apply -f deploy/kubernetes/web.yaml
kubectl apply -f deploy/kubernetes/network-policy.yaml
```

## Release gate

- Image vulnerability scan, dependency review, and signed build provenance pass.
- `AUTH_REQUIRED=true`, a strong JWT secret, TLS ingress, and allowed origins are configured.
- Database uses PostGIS, backups, encryption, and a non-superuser application account.
- Audit export reaches the organisation's logging platform and has a tested retention policy.
- ICJS legal/data-sharing approval, gateway contract, data mapping, and penetration test are accepted.
- Model monitoring, human-review ownership, and rollback procedures have named operators.
