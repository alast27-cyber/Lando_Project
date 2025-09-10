# Autoscaling Setup for Lando

This repo enables pod- and cluster-level autoscaling.

- HPA uses CPU utilization and external metric `http_requests_per_pod`.
- Prometheus Adapter maps Prometheus series into external metrics.
- Cluster Autoscaler is installed provider-specific (AWS, GKE, Azure).

## Secrets required
- KUBECONFIG_DATA
- CLOUD_PROVIDER
- CLUSTER_NAME
- SERVICE_URL
- SLACK_WEBHOOK_URL (optional)
