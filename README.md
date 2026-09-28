for airflow docker container, inside the `airflow` directory:
```bash
 FERNET_KEY=$(uv run python -c \
'import base64, secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())')
```

and

```bash
cat > .env <<EOF
AIRFLOW_UID=$(id -u)
FERNET_KEY=${FERNET_KEY}
EOF
```

- AIRFLOW_UID controls which user Airflow's containers use when writing files into directories mounted from your Mac. The official Airflow tutorial creates .env with an AIRFLOW_UID for its Docker Compose setup
- FERNET_KEY: Airflow uses Fernet encryption to encrypt sensitive values such as connection passwords and variables stored in its metadata database.

See the `.env.example` file
