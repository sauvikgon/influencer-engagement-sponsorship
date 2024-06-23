from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

# Create the Flask application
app = create_app()

# Create a new application context
with app.app_context():
    # Check if the 'Public' influencer already exists
    public_influencer = User.query.filter_by(username='Public').first()
    
    if not public_influencer:
        # Create a new 'Public' influencer
        public_influencer = User(
            username='Public',
            email='public@example.com',
            password_hash=generate_password_hash('publicpassword'),  # Replace with a secure password
            role='influencer',
            industry='',
            platforms='',
            category='',
            niche='',
            profile_pic='default.png',
            flag=False
        )
        
        # Add the new influencer to the session and commit
        db.session.add(public_influencer)
        db.session.commit()
        
        print('Public influencer created successfully.')
    else:
        print('Public influencer already exists.')
