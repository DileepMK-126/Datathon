# Sentinel governance and ICJS integration gate

Sentinel must not ingest operational criminal-justice records until the deploying agency completes this gate. The code enforces the technical controls below, but it cannot grant legal authority or access on the agency's behalf.

## Required before any real-data connection

1. Obtain the approved ICJS/NCRB/NIC integration contract: base URL, API version, field schema, OAuth method, certificate requirements, service-account scope, and rate limits.
2. Obtain the authorised data-sharing approval and document the permitted purpose in `ICJS_LEGAL_BASIS`.
3. Complete a data-protection impact assessment, retention schedule, operator access matrix, and incident-response plan.
4. Store `ICJS_CLIENT_SECRET`, `JWT_SECRET`, database credentials, and `DATA_ENCRYPTION_KEY` in an agency-managed secrets service—never in Git, browser storage, or a deployment manifest.
5. Validate the approved field mapping against the ICJS data-sharing matrix in a non-production environment.
6. Run independent security testing, model-bias evaluation, calibration checks, and sign-off from the responsible authority.

## Controls implemented in this repository

- **PostGIS option:** `DATABASE_URL` activates PostgreSQL/PostGIS, creates a WGS84 `geom` column and GiST spatial index, and uses the geometry index for bounded map queries.
- **Authentication and roles:** production uses signed, short-lived JWTs. Analyst, supervisor, and administrator roles are checked on each endpoint. Audit access and ICJS operations require administrator role.
- **Audit events:** API activity is recorded with actor, role, endpoint, outcome, request ID, and timestamp. Tokens, passwords, query strings, and raw payloads are excluded.
- **Data minimisation:** the ICJS adapter stores only a small approved analytical projection in clear text; the original source record is encrypted with Fernet before it reaches the staging table.
- **No silent sync:** `ICJS_ENABLED=false` is the default. When disabled or incompletely configured, the sync endpoint returns `503` and performs no external request.
- **Human review:** all model outputs and entity links remain decision-support leads, never evidence or an automated enforcement action.

## ICJS adapter activation

After the gate is approved, configure the secret store with the variables in `.env.example`, set `ICJS_ENABLED=true`, and set the agency-approved `ICJS_CASES_PATH`. The adapter expects OAuth client credentials and a JSON collection from the agreed case endpoint. It stages data as `pending_review`; it deliberately does not promote source records into analytics until a separately approved mapping and review workflow is implemented.

The public ICJS material describes a stakeholder API gateway and a data-sharing matrix, so the final endpoint and schema must come from the authorised integration team rather than be guessed. See the [ICJS portal](https://icjs.gov.in/ICJS/) and [MHA ICJS overview](https://www.mha.gov.in/en/commoncontent/inter-operable-criminal-justice-system-icjs).

## Operational controls outside code

Deploying agency responsibilities include managed database backups and encryption, key rotation, SIEM export and alerting, immutable backup retention, network segmentation, endpoint protection, annual access recertification, and a lawful process for data-subject, correction, and retention requests where applicable.
