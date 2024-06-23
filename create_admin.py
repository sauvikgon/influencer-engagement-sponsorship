from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

# Create a new application context
with app.app_context():
    # Check if the 'admin' user already exists
    admin_user = User.query.filter_by(username='admin').first()
    
    if not admin_user:
        # Create a new 'admin' user
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('adminpassword'),  # Replace with a secure password
            role='admin',
            industry='',
            platforms='',
            category='',
            niche='',
            profile_pic='default.png',
            flag=False
        )
        
        # Add the new admin to the session and commit
        db.session.add(admin_user)
        db.session.commit()
        
        print('Admin user created successfully.')
    else:
        print('Admin user already exists.')