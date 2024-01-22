Brendan is responsible for observing Entra ID Groups and granting/removing access to Azure Database for PostgreSQL Servers.

# SQL Statements

## Create User:

```sql
SELECT * FROM pgaadauth_create_principal('njames@bink.com', false, false);
GRANT pg_read_all_data TO "njames@bink.com";
```

## Delete User:

```sql
DROP role "njames@bink.com";
```


## Query Users:

```sql
SELECT usename FROM pg_catalog.pg_user WHERE usename LIKE '%bink.com';
```

```sql
SELECT rolname FROM pgaadauth_list_principals(false);
```


## Connect as Brendan:

```python
import psycopg2
from azure.identity import DefaultAzureCredential


azure_credential = DefaultAzureCredential()
token = azure_credential.get_token("https://ossrdbms-aad.database.windows.net/.default")
conn_str = f"postgresql://uksouth-dev-hermes:{token.token}@uksouth-dev-n71o.postgres.database.azure.com/postgres?sslmode=require"
conn = psycopg2.connect(conn_str)

```
