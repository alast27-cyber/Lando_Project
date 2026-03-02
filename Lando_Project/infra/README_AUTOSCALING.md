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

## Required Secrets
- `KUBECONFIG_DATA`
- `CLOUD_PROVIDER`
- `CLUSTER_NAME`
- `SERVICE_URL`
- `SLACK_WEBHOOK_URL` (optional)
