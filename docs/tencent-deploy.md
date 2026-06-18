# Tencent Lightweight Cloud Deployment

This project can run on the Tencent Ubuntu 22.04 Docker image with Docker Compose.

## 1. Open firewall ports

In the Tencent Cloud console, allow inbound TCP port `80`.

If you later bind a domain and enable HTTPS, also allow TCP port `443`.

## 2. Get code from GitHub

On the server:

```bash
sudo mkdir -p /opt
cd /opt/insurance-django
```

For the first deployment, clone the repository:

```bash
cd /opt
sudo git clone https://github.com/feiyangyang/insurance-django.git
sudo chown -R ubuntu:ubuntu /opt/insurance-django
cd /opt/insurance-django
```

If `/opt/insurance-django` already exists from an earlier tarball deployment, replace it with a Git clone:

```bash
cd /opt
sudo docker compose -f /opt/insurance-django/docker-compose.yml down || true
sudo rm -rf /opt/insurance-django
sudo git clone https://github.com/feiyangyang/insurance-django.git
sudo chown -R ubuntu:ubuntu /opt/insurance-django
cd /opt/insurance-django
```

## 3. Create production env

```bash
cp .env.example .env
python3 - <<'PY'
from pathlib import Path
from secrets import token_urlsafe

env = Path(".env")
text = env.read_text()
text = text.replace("replace-this-with-a-long-random-secret", token_urlsafe(50))
env.write_text(text)
PY
nano .env
```

Set:

- `ALLOWED_HOSTS` to your server public IP and domain, separated by commas.
- `CSRF_TRUSTED_ORIGINS` to `http://your-ip` and, if you have a domain, `https://your-domain`.
- Keep the `SECURE_*` values as `False`/`0` when you are only using HTTP by IP.
- After you configure HTTPS, set `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`, and `SECURE_HSTS_SECONDS=31536000`.
- Only set `SECURE_HSTS_INCLUDE_SUBDOMAINS=True` and `SECURE_HSTS_PRELOAD=True` when every subdomain is permanently HTTPS-ready.

## 4. Start

```bash
docker compose up -d --build
docker compose logs -f web
```

Visit:

```text
http://your-server-ip/
```

## 5. Create admin user

```bash
docker compose exec web python manage.py createsuperuser
```

## 6. Update later

Commit and push changes from your local machine:

```bash
git add .
git commit -m "Describe the release"
git push origin main
```

Then deploy on the server:

```bash
cd /opt/insurance-django
git pull origin main
docker compose up -d --build
docker compose ps
```

The SQLite database is stored in the Docker volume `insurance-django_app_data`.
Current demo data is not backed up by this workflow.
