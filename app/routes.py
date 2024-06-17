from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.models import User, Campaign, AdRequest
# from app.forms import RegistrationForm, LoginForm, CampaignForm, AdRequestForm
from app.forms import SponsorRegistrationForm, InfluencerRegistrationForm, LoginForm, CampaignForm, AdRequestForm
from werkzeug.security import generate_password_hash

main = Blueprint('main', __name__)

# # We have commented this because this wwas showing home page we need to show loginpage
# @main.route('/')
# @main.route('/home')
# def home():
#     return render_template('home-new.html')

@main.route('/')
@main.route('/home')
def home():
    form = LoginForm()  # Replace with your actual form class
    return render_template('home-new.html', form=form)

# @main.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
#         user = User(username=form.username.data, email=form.email.data, password=hashed_password, role=form.role.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Your account has been created! You are now able to log in', 'success')
#         return redirect(url_for('main.login'))
#     return render_template('register.html', title='Register', form=form)

@main.route('/register/sponsor', methods=['GET', 'POST'])
def register_sponsor():
    form = SponsorRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='sponsor')
        user.set_password(form.password.data)
        user.industry = form.industry.data
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered as a sponsor.')
        return redirect(url_for('main.login'))
    return render_template('register_sponsor.html', form=form)

@main.route('/register/influencer', methods=['GET', 'POST'])
def register_influencer():
    form = InfluencerRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='influencer')
        user.set_password(form.password.data)
        user.platforms = form.platforms.data
        user.category = form.category.data
        user.niche = form.niche.data
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered as an influencer.')
        return redirect(url_for('main.login'))
    return render_template('register_influencer.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('main.admin_info'))
    elif current_user.role == 'sponsor':
        return redirect(url_for('main.sponsor_profile'))
    elif current_user.role == 'influencer':
        return redirect(url_for('main.influencer_profile'))
    return redirect(url_for('main.home'))


@main.route('/campaign/new', methods=['GET', 'POST'])
@login_required
def new_campaign():
    form = CampaignForm()
    if form.validate_on_submit():
        campaign = Campaign(name=form.name.data, description=form.description.data, budget=form.budget.data, visibility=form.visibility.data, user_id=current_user.id)
        db.session.add(campaign)
        db.session.commit()
        flash('Your campaign has been created!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('create_campaign.html', title='New Campaign', form=form)

@main.route('/ad_request/new/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def new_ad_request(campaign_id):
    form = AdRequestForm()
    if form.validate_on_submit():
        ad_request = AdRequest(campaign_id=campaign_id, influencer_id=current_user.id, requirements=form.requirements.data, payment_amount=form.payment_amount.data, status='Pending')
        db.session.add(ad_request)
        db.session.commit()
        flash('Your ad request has been created!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('create_ad_request.html', title='New Ad Request', form=form, campaign_id=campaign_id)

@main.route('/sponsor/profile')
@login_required
def sponsor_profile():
    if current_user.role == 'sponsor':
        return render_template('sponsor_profile.html')
    return redirect(url_for('main.home'))

# # There was a error with code. So we had to modify it below
# @main.route('/sponsor/campaigns')
# @login_required
# def sponsor_campaigns():
#     if current_user.role == 'sponsor':
#         campaigns = Campaign.query.filter_by(owner=current_user).all()
#         return render_template('sponsor_campaigns.html', campaigns=campaigns)
#     return redirect(url_for('main.home'))

@main.route('/sponsor/campaigns')
@login_required
def sponsor_campaigns():
    if current_user.role == 'sponsor':
        campaigns = Campaign.query.filter_by(user_id=current_user.id).all()
        return render_template('sponsor_campaigns.html', campaigns=campaigns)
    return redirect(url_for('main.home'))


@main.route('/sponsor/find')
@login_required
def sponsor_find():
    if current_user.role == 'sponsor':
        return render_template('sponsor_find.html')
    return redirect(url_for('main.home'))

@main.route('/sponsor/stats')
@login_required
def sponsor_stats():
    if current_user.role == 'sponsor':
        # You may need to add logic to gather relevant stats
        return render_template('sponsor_stats.html')
    return redirect(url_for('main.home'))


# For Influencers
@main.route('/influencer/profile')
@login_required
def influencer_profile():
    if current_user.role == 'influencer':
        return render_template('influencer_profile.html')
    return redirect(url_for('main.home'))

@main.route('/influencer/find')
@login_required
def influencer_find():
    if current_user.role == 'influencer':
        return render_template('influencer_find.html')
    return redirect(url_for('main.home'))

@main.route('/influencer/stats')
@login_required
def influencer_stats():
    if current_user.role == 'influencer':
        return render_template('influencer_stats.html')
    return redirect(url_for('main.home'))

# For Admins
@main.route('/admin/info')
@login_required
def admin_info():
    if current_user.role == 'admin':
        users = User.query.all()
        campaigns = Campaign.query.all()
        ad_requests = AdRequest.query.all()
        return render_template('admin_info.html', users=users, campaigns=campaigns, ad_requests=ad_requests)
    return redirect(url_for('main.home'))

@main.route('/admin/find')
@login_required
def admin_find():
    if current_user.role == 'admin':
        return render_template('admin_find.html')
    return redirect(url_for('main.home'))

@main.route('/admin/stats')
@login_required
def admin_stats():
    if current_user.role == 'admin':
        return render_template('admin_stats.html')
    return redirect(url_for('main.home'))
