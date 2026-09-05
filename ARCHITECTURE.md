# Architecture

## Objective (recap)
Automate weekly collection of international cricket matches and generate
shareable images (landscape for X/Twitter, square for Instagram). Runs
weekly, recommended Tuesday 10:00 AM UTC. See root `CLAUDE.md` for full
scope rules (international matches only, formats included/excluded).

## Pipeline
```
Scheduled Trigger (GitHub Actions cron)
        ↓
Web Scraper (now CricAPI JSON, was ESPNCricinfo scraping — see root
        CLAUDE.md "Current status" for why)
        ↓
Data Parser & Filter (international matches only)
        ↓
Image Generator (PIL/Pillow)
        ↓
Store image in repo /output/
        ↓
Manual upload to X & Instagram (MVP) → API integration later
```

## Repo structure to scaffold (Phase 1)
```
cricket-match-agent/
├── src/
│   ├── scraper.py          # CricAPI scraper (was ESPNCricinfo scraper)
│   ├── parser.py           # data parsing & filtering
│   ├── image_generator.py  # image creation
│   └── utils.py            # helper functions
├── output/                 # weekly generated images
├── config/
│   └── settings.py         # URLs, constants, config
├── tests/                  # unit tests
├── requirements.txt
├── README.md
├── .gitignore              # venv/, __pycache__/, .env, output/
└── .github/
    └── workflows/
        ├── weekly-scrape.yml
        └── ci.yml
```

## Build order (phases)
1. Repo + venv + folder structure + git
2. Scraper + parser + data model
3. Image generator (landscape + square templates)
4. GitHub Actions automation (weekly cron)
5. Manual social upload workflow (API integration later, optional)
6. Tests (unit + integration, target >80% coverage)
7. Kubernetes + AWS hosting exercise (one-time portfolio/learning build,
   detailed in "Kubernetes + AWS hosting (one-time exercise)" below) —
   each sub-phase depends on the previous one completing; GitHub Actions
   (phase 4) remains the permanent production scheduler throughout and
   after this exercise, since the app doesn't technically need this
   infrastructure — see that section's "Technical fit honesty" note.

See root `CLAUDE.md` → "Current status" for which phases are actually done.

## Kubernetes + AWS hosting (one-time exercise)

**Purpose:** hands-on EKS/Kubernetes/Terraform/AWS-IAM experience for the
user's Senior SRE career goal — not a production necessity. The app runs
correctly and for $0 today via the phase 4 GitHub Actions cron; that stays
the permanent scheduler. This is built, demonstrated, documented, and torn
down (`terraform destroy`) within a single bounded session (~3-4 hours) so
the real AWS spend is roughly **$2-5 total** (EKS's control-plane fee bills
per hour, not per month) rather than the ~$74-75/month an always-on cluster
would cost. Avoid adding a NAT Gateway (~$0.045/hr + data processing) — use
a public subnet with a locked-down security group instead, since the
workload is a batch job with no inbound listener.

Each phase below depends on the prior one completing:

7.1. **Terraform bootstrap** — S3 state bucket + DynamoDB lock table
     (one-time, local state).
7.2. **Terraform — VPC** — public subnets across 2 AZs (EKS requires ≥2),
     internet gateway, restrictive security group (HTTPS egress only, no
     inbound). No NAT Gateway.
7.3. **Terraform — ECR** — repository with `scan_on_push = true`.
7.4. **CI — build and push** — new job in `.github/workflows/ci.yml`,
     gated on `main` and on tests passing, authenticating via GitHub OIDC
     (no static AWS keys in GitHub secrets), that builds
     `src/Dockerfile` (root build context) and pushes to ECR. Verify an
     image lands in ECR before touching Kubernetes at all.
7.5. **Terraform — EKS** — cluster + Fargate profile (namespace
     `cricket-agent`, no managed node group — Fargate avoids paying for an
     idle EC2 node between runs) + OIDC provider for IRSA + KMS encryption
     for Kubernetes Secrets.
7.6. **Terraform — S3 + IRSA** — private images bucket (all public access
     blocked) + IAM role scoped to that bucket's prefix, trusted only by
     the `cricket-agent-sa` ServiceAccount; annotate the ServiceAccount
     with the role ARN.
7.7. **Code change — S3 upload** — add a `boto3` upload step to `main.py`
     after `generate_images()` (nothing today persists the generated PNGs
     anywhere — this closes a real existing gap, independent of which
     scheduler runs it). Test locally against a real bucket first.
7.8. **Terraform — secret** — SSM `SecureString` parameter for
     `CRICAPI_KEY` (Standard tier, $0/month); extend
     `config/settings.py` to fetch it via `boto3` when not in
     `development` mode; extend the IRSA policy with `ssm:GetParameter`
     scoped to that one parameter.
7.9. **CronJob manifest** — `k8s/cronjob.yaml` (or defined via Terraform's
     `kubernetes` provider for single-command apply/destroy),
     `schedule: "0 10 * * 2"`, `concurrencyPolicy: Forbid`,
     `backoffLimit: 2`, `timeZone: "Etc/UTC"` — mirrors the phase 4 cron
     schedule on a different scheduler.
7.10. **Manual trigger + verify** — force a run with
      `kubectl create job --from=cronjob/...` (don't wait for Tuesday);
      confirm exit code 0, S3 upload landed, and logs appear in
      CloudWatch (Fargate routes stdout/stderr there for free — no
      Container Insights/Prometheus needed for a one-time check).
7.11. **Document** — screenshots, architecture note, actual cost from
      Billing/Cost Explorer, commit Terraform code and manifests to the
      repo with a short "how to redeploy for a demo" runbook (~15 min to
      reapply).
7.12. **Terraform destroy** — tear down the same day to stop billing;
      confirm in the AWS Console that the EKS cluster, Fargate profile,
      and VPC resources are gone.

## Automation (live)
Two GitHub Actions workflows are committed under `.github/workflows/`
(added in `78f39a6`):

- **`weekly-scrape.yml`** — runs on the Tuesday 10:00 UTC cron
  (`0 10 * * 2`) plus manual `workflow_dispatch`. Installs deps, injects
  `CRICAPI_KEY` from the repo secret, runs `python main.py`, and uploads
  `output/matches.json` as a build artifact.
- **`ci.yml`** — runs on every push/PR to `main`. Installs deps, runs
  `pytest`, then `flake8` (lint step is `continue-on-error: true` —
  informational only for now, not a required gate).

GitHub Actions free tier (2,000 min/month) is more than sufficient for a
weekly job plus per-push CI.
