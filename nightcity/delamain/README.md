# Delamain

## Config File

The delamain config file should be placed in the project root, locally, or in `/var/config/delamain.yaml` within Kubernetes.

Example File:
```yaml
dns_rewites:
  a:
    - uksouth-staging-2o6h.postgres.database.azure.com
    - uksouth-staging-q263.redis.cache.windows.net
  cname:
    - name: staging.uksouth.bink.sh
      record: uksouth-staging-traefik.alpine-monster.ts.net

```
