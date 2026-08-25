# Aida Hotel

Multilingual hotel website for **Aida Hotel, Bukhara** — online booking, admin-managed content, and room availability (HTMX).

## Features

- **3 languages**: Uzbek (default), Russian, English
- **Admin CMS**: images, rooms, prices, content — no code required
- **Online booking** with live room availability grid (HTMX)
- **Reference codes** e.g. `AIDA-2026-0042`
- **Seasonal pricing**, blocked dates, promotions
- **SEO**: sitemap, robots.txt, Open Graph, Google Analytics & Yandex Metrika (via admin)

## Requirements

- Python 3.11+
- See `requirements.txt`

## Setup

```bash
cd "aida hotel"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py compile_i18n
python manage.py runserver
```

Optional demo data: `python manage.py seed_demo`

- Site: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Admin content

Upload via **Site settings**, **Hero slides**, **Gallery**, **Room types** (with room numbers & images), **Bookings**, etc. All translatable fields have UZ/RU/EN tabs.

## Tests

```bash
python manage.py test hotel -v 2
```

## Production checklist

```bash
# .env
DEBUG=False
SECRET_KEY=your-long-random-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

python manage.py collectstatic --noinput
python manage.py migrate
```

Use PostgreSQL or MySQL instead of SQLite for production. Ensure `media/` is writable and served.

## Project structure

- `config/` — settings, URLs
- `hotel/` — models, views, services, admin, sitemaps
- `templates/` — HTML + HTMX partials
- `static/` — CSS, JS
- `locale/` — UI translations (`compile_i18n` command)
- `media/` — uploaded images (admin)

## Notes

- No payment gateway or email notifications (by design)
- Coordinates & map: set in **Site settings** → Location
