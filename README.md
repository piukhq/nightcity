# Night City

A collection of DevOps Scripts and Helper Tools

## Command Matrix

| name | description |
| ---- | ----------- |
| [Delamain](nightcity/delamain/README.md) | Lookup DNS Records inside Kubernetes and report the results back to NextDNS |
| [Brendan](nightcity/brendan/README.md) | Create / Delete users in PostgreSQL based on Entra ID Group Membership |

## TODO

* Improve how `pydantic-settings` is implemented, the Typer/Click CLI enforces that all environment variables be set, when only _some_ are required.
