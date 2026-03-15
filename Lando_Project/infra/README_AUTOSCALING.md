# Lando AIOS Alignment Guide

This repository implements autoscaling controls that can act as the resource-regulation
backplane for the **Instinctive Artificial Intelligence (IAI)** concept in an
AI-Native Operating System (AIOS).

## Concept-to-Implementation Mapping

### 1) Instinct First Principle
- The HPA policy provides low-latency, automatic responses to load variation.
- External metric-based scaling (`http_requests_per_pod`) acts as a reflex signal,
  analogous to an Instinctive Problem Solving (IPS) trigger.

### 2) Energy Conservation and Homeostasis
- CPU utilization targeting (`averageUtilization: 50`) captures thermal/compute pressure
  and keeps the system in a stable operating envelope.
- Request-rate targeting (`averageValue: "10"`) avoids unnecessary over-scaling,
  preserving cluster energy and cost.

### 3) Physics and Dialectics Framing
The runtime policy can be interpreted through the IAI blueprint:
- **Duality (Action/Reaction, Wave-Particle)**: incoming request waves and service
  resource reaction are balanced by autoscaling feedback loops.
- **Contradictions (Internal vs. External)**:
  - Internal contradiction: pod CPU saturation.
  - External contradiction: external request pressure.
  - Inter-relational contradiction: mismatch between current replicas and demand trend.

### 4) Layered Functional Analogy
- **ILL (Intuitive Learning Layer)**: telemetry ingest through Prometheus metrics.
- **IPS Layer**: HPA acts on known patterns quickly via pre-defined scaling rules.
- **CLL (Cognition Layer)**: future extension point for advanced policy synthesis
  (for example, adding new external metrics or adaptive thresholds).

### 5) Energy Minimization Driver (EMD)
The current stack supports EMD-style optimization by preferring lightweight,
repeatable reactions over expensive global interventions.

## Current Repository Components
- `Lando_Project/monitoring/prometheus-adapter-config.yaml`
  - Maps Prometheus query outputs into external metrics consumable by the HPA.
- `Lando_Project/helm/templates/hpa.yaml`
  - Defines resource + external-metric autoscaling behavior.
- `.github/workflows/prometheus-rules-test.yml`
  - Validates manifests and confirms core metric/doc assumptions in CI.

## Deployment and Verification Workflow

### Prerequisites
1. Kubernetes cluster with metrics-server installed.
2. Prometheus + Prometheus Adapter available in-cluster.
3. Helm release values aligned with expected metric names.

### Apply Flow
1. Apply/update adapter rules from `Lando_Project/monitoring/prometheus-adapter-config.yaml`.
2. Deploy the HPA from `Lando_Project/helm/templates/hpa.yaml`.
3. Confirm HPA external metrics are discovered:
   ```bash
   kubectl get --raw "/apis/external.metrics.k8s.io/v1beta1" | jq .
   ```
4. Confirm your target external metric resolves:
   ```bash
   kubectl get --raw "/apis/external.metrics.k8s.io/v1beta1/namespaces/default/http_requests_per_pod" | jq .
   ```

### Runtime Validation
- Check HPA decision data:
  ```bash
  kubectl describe hpa <your-hpa-name>
  ```
- Watch replica adjustments:
  ```bash
  kubectl get hpa -w
  ```
- Inspect target workload scaling behavior:
  ```bash
  kubectl get deploy <your-workload> -w
  ```

## Troubleshooting Playbook

### Symptom: `FailedGetExternalMetric`
Possible causes:
- Adapter query is returning no series.
- Metric labels do not match the HPA selector namespace.
- Prometheus scrape target is missing or stale.

Checks:
- Review adapter logs for query errors.
- Run the equivalent query directly in Prometheus.
- Confirm metric name and labels in adapter config match HPA expectations.

### Symptom: HPA never scales above minimum replicas
Possible causes:
- Metric value is below threshold (`averageValue: "10"`).
- CPU target too high for observed load profile.
- Workload requests are oversized, reducing utilization percentage.

Checks:
- Compare actual traffic/load to configured thresholds.
- Tune `averageValue` and/or `averageUtilization` conservatively.
- Validate container resource requests are realistic.

### Symptom: Oscillation (rapid up/down scaling)
Possible causes:
- Spiky request metric without smoothing.
- Insufficient stabilization windows or cooldown behavior.

Checks:
- Add or tune HPA behavior policies.
- Smooth external metric at query level (for example, rate windows).
- Observe scale events over a longer period before retuning.

## CI and Issue Tracking Notes
- CI guardrails run from `.github/workflows/prometheus-rules-test.yml`.
- Issue tracking for IAI and deployment follow-ups is maintained in
  `Lando_Project/infra/ISSUE_STATUS.md`.

## Required Secrets
- `KUBECONFIG_DATA`
- `CLOUD_PROVIDER`
- `CLUSTER_NAME`
- `SERVICE_URL`
- `SLACK_WEBHOOK_URL` (optional)
