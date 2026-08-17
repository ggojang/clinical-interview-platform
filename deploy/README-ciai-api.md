# Clinical Interview API staging deployment

The collaboration source of truth is GitLab. The `banttas-ai` host runs the
same committed revision as a rootless Podman container managed by systemd
Quadlet. Do not edit application source inside the running container.

## Host assumptions

- rootless Podman 5.x
- service account: `banttas-ai`
- staging listener: `10.20.0.12:9090`
- existing STOM, LLM, and zone TLS services remain unchanged
- API access is restricted to the private Tailscale/zone network

## Build and install

From the repository root on the host:

```bash
podman build -t localhost/ciai-api:staging -f services/interview_api/Dockerfile .
install -m 0644 deploy/ciai-api.container ~/.config/containers/systemd/ciai-api.container
systemctl --user daemon-reload
systemctl --user enable --now ciai-api.service
```

Create the API key secret once, without placing the value in the repository or
the Quadlet file:

```bash
umask 077
openssl rand -hex 32 > ~/.config/ciai/api-key
podman secret create ciai-api-key ~/.config/ciai/api-key
```

## Verify

```bash
systemctl --user --no-pager status ciai-api.service
podman healthcheck run ciai-api
curl -fsS http://10.20.0.12:9090/healthz
```

The current container is a staging runtime. It stores response-bearing state
only in process memory, purges it on TTL/close/shutdown, and exposes only the
implemented `clinical_adaptive` mode. FHIR artifacts, execution-order APIs,
persistent job state, requester/participant authorization separation, and
artifact ingestion are subsequent milestones and must not be advertised as
implemented.
