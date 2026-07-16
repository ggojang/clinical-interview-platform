# Anonymous Research Feedback Worker

This optional Cloudflare Worker records one content-free anonymous start event after the first user message and receives explicitly consented structured end-of-test metrics. It never accepts interview answers, transcripts, files, free text, direct identifiers, demographics, network identifiers, or contact data.

The existing GitHub Pages Knowledge Action remains read-only. This service is a separate write boundary with separate authentication, retention, and privacy controls.

The current research deployment is `https://clinical-interview-feedback.seungjong-yu.workers.dev`. Earlier chats are not recoverable. A page view without a user message cannot invoke a Custom GPT Action; the earliest observable event is the first message. Detailed end-of-session feedback remains separately consented.

## Deploy

Prerequisites are a Cloudflare account, Wrangler, and a Workers/D1-capable project.

```bash
cd services/feedback-worker
cp wrangler.toml.example wrangler.toml
npx wrangler d1 create clinical-interview-feedback
```

Put the returned D1 database identifier in the local `wrangler.toml`. Do not commit that file. Then configure two different random secrets of at least 24 characters:

```bash
npx wrangler secret put FEEDBACK_WRITE_KEY
npx wrangler secret put FEEDBACK_ADMIN_KEY
npx wrangler d1 migrations apply clinical-interview-feedback --remote
npx wrangler deploy
```

`FEEDBACK_WRITE_KEY` is configured as the Custom GPT Action API key in header `X-Feedback-Key`. `FEEDBACK_ADMIN_KEY` is never configured in ChatGPT and is used only by the local statistics client.

After deployment, render the Action schema with the actual HTTPS origin:

```bash
python ../../tools/feedback/render_openapi.py \
  --base-url https://your-worker-host \
  --output /tmp/feedback-openapi.yaml
```

Import the rendered schema as a separate Custom GPT Action, set API-key authentication, use the public GitHub Pages privacy notice, and save/update the GPT. Repository deployment alone does not alter the GPT editor.

## Read statistics

```bash
python3 tools/feedback/fetch_stats.py --days 30
```

The deployed local setup reads the administrator key from `~/.config/clinical-interview-platform/feedback-admin-key`, which must remain mode `0600`. `FEEDBACK_API_BASE_URL`, `FEEDBACK_ADMIN_KEY`, and `FEEDBACK_ADMIN_KEY_FILE` remain available as explicit overrides. Never commit the key file.

Statistics report anonymous sessions started after a first message, separately consented detailed submissions, and the submission rate. A session abandoned after the first message remains visible as a start count. A browser view with no message is not observable through the Action, so ChatGPT's coarse `Chats` count remains the only approximate page-level measure.

## Retention and deletion

Rows are deleted by the scheduled Worker after `RETENTION_DAYS`, default 90. Aggregates are computed on request and are not automatically committed to this repository. If an aggregate informs a Knowledge change, only a sufficiently de-identified generalized candidate may enter the Build-Time feedback workflow.

## Test

```bash
npm test
```
