from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    hashed_password = generate_password_hash('adminpassword', method='pbkdf2:sha256')
    admin = User(username='admin', email='admin@example.com', password=hashed_password, role='admin')
    db.session.add(admin)
    db.session.commit()
