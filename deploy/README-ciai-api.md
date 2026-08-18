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
- the API container uses host networking but binds only `10.20.0.12:9090`, so
  it can reach the host-only LLM at `127.0.0.1:8000`

The `/demo-api` surface is exposed without an API key for synthetic public
tests at `https://ciai.banttas.com`. It is separately bounded to the
platform-local LLM, memory-only sessions, a ten-minute TTL, a concurrent-session
cap, and global request limits. The authenticated `/v1` API remains protected.
`deploy/traefik-ciai.yml` is the source-controlled public edge route; install it
as `ciai.yml` in the production Traefik file-provider directory. The edge adds
HTTPS, security headers, compression, request-rate and in-flight limits. A WAF
is not yet present and remains a production-hardening requirement.

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

The demo also exposes a read-only, fixed-upstream terminology proxy at
`/demo-api/terminology`. The container uses STOM's Tailscale-bound internal
listener at `http://10.20.0.12:8443/fhir`; it does not hairpin through the
public edge. Only ValueSet canonical/filter/count values are sent to STOM.
QuestionnaireResponse data and participant answers are never sent to the
terminology server. Missing ValueSets remain unresolved instead of receiving
invented answer options.

## LLM providers

The Quadlet enables question presentation through the local OpenAI-compatible
endpoint by default:

```text
provider: local_vllm
endpoint: http://127.0.0.1:8000/v1
model: qwen3-27b
```

The existing `vllm-api-key` Podman secret is injected into the API container as
`CLINICAL_LLM_LOCAL_API_KEY`. The value is never copied to Git or returned by
the API.

The adaptive interview uses two model calls per turn. A read-only retrieval
call receives the selected RFE package index and the full in-memory
conversation, then returns only Question, Fact, and priority Rule ids. The
patient-facing generation call receives `docs/gpt/GPT_INSTRUCTIONS.md`
verbatim, the exact repository objects for those ids, every safety Rule in the
package, and the full conversation. This preserves the 61 KB instruction
contract without putting every full package object into the local model's
context at once. It is the Action-style conversation-native orchestration used
by the Custom GPT test: the model maintains semantic coverage and chooses one
next question with its answer shortcuts. The opening symptom remains part of
the conversation, so already stated site, laterality and symptom meaning are
not discarded before Q1. The API parses visible Q references only for UI and
draft FHIR history; it does not replace the model's question with a
deterministic planner.

There is no legacy deterministic question-selection fallback. If the selected
LLM or required Knowledge payload is unavailable, the API returns a temporary
service error and leaves the interview in progress instead of silently
switching to the previous engine. Response-bearing conversation state remains
memory-only and is purged on close or TTL expiry.

To offer a commercial OpenAI-compatible provider, add only non-secret metadata
to `CLINICAL_LLM_PROVIDERS_JSON` and inject the named credential as a Podman
secret. For example, use an administrator-approved provider id and model; do
not copy this placeholder literally:

```json
[
  {
    "provider_id": "commercial_approved",
    "display_name": "Approved commercial LLM",
    "adapter": "openai_compatible_chat",
    "base_url": "https://vendor.example/v1",
    "model": "approved-model-id",
    "external_processing": true,
    "api_key_env": "COMMERCIAL_APPROVED_API_KEY",
    "enabled": true
  }
]
```

Never put the credential value in Git, the JSON configuration, request bodies,
or logs. External selection is rejected unless the provider is configured,
requester policy permits it, and explicit external-processing consent is true.
