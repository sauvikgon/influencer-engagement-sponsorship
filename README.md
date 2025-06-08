# Influencer Engagement & Sponsorship

This Flask application lets sponsors connect with influencers. It uses SQLite for development and includes scripts to create admin and public users.

## Local Development

1. Create and activate a virtual environment.
2. Install requirements:

```bash
pip install -r requirements.txt
```

3. Initialize the database:

```bash
python create_admin.py
python create_public_user.py
```

4. Run the application for testing:

```bash
python run.py
```

## Production Hosting

To run the application in production, use a WSGI server like **gunicorn** behind a reverse proxy (e.g., Nginx). Set the `FLASK_APP` environment variable to `run.py` and run:

```bash
pip install gunicorn
gunicorn run:app
```

You can configure Nginx or another proxy to forward HTTP requests to `gunicorn` and serve static files from `app/static`.

Set the `SECRET_KEY` and other configuration as environment variables before starting the server. For persistent storage, replace the SQLite URI in `app/__init__.py` with a production database (such as PostgreSQL).

