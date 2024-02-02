# Night City

A collection of DevOps Scripts and Helper Tools

## Command Matrix

| name | description |
| ---- | ----------- |
| [Delamain](nightcity/delamain/README.md) | Lookup DNS Records inside Kubernetes and report the results back to NextDNS |
| [Brendan](nightcity/brendan/README.md) | Create / Delete users in PostgreSQL based on Entra ID Group Membership |

## Environment Variables

| Name | Description | Default |
| ---- | ----------- | ------- |
| `NEXTDNS_API_KEY` | The NextDNS API Key | None |
| `NEXTDNS_ID` | The NextDNS Profile ID | None |
| `LOG_LEVEL` | The Log Level for the Application | `INFO` |

## TODO

* Move all configuration to Azure App Config
