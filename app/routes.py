from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.models import User, Campaign, AdRequest
# from app.forms import RegistrationForm, LoginForm, CampaignForm, AdRequestForm
from app.forms import SponsorRegistrationForm, InfluencerRegistrationForm, LoginForm, CampaignForm, AdRequestForm
from sqlalchemy import and_,or_
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import date, datetime, timedelta
from collections import defaultdict
import os
import uuid

main = Blueprint('main', __name__)

# # We have commented this because this was showing home page we need to show loginpage
# @main.route('/')
# @main.route('/home')
# def home():
#     return render_template('home.html')

@main.route('/')
# @main.route('/home')
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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.role == "admin":  # Assuming `is_admin` is a property of your user model
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

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
        return redirect(url_for('main.home'))
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
        return redirect(url_for('main.home'))
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
    return render_template('home-new.html', form=form)

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
        campaign = Campaign(name=form.name.data, description=form.description.data, budget=form.budget.data, visibility=form.visibility.data, start_date=form.start_date.data, end_date=form.end_date.data, user_id=current_user.id)
        db.session.add(campaign)
        db.session.commit()
        flash('Your campaign has been created!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('create_campaign.html', title='New Campaign', form=form)

@main.route('/campaign/flag/<int:id>', methods=['POST'])
@login_required
@admin_required
def flag_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    
    # Update the flag field
    campaign.flag = True
    db.session.commit()
    
    flash('The campaign has been flagged!', 'success')
    return redirect(url_for('main.admin_info'))

@main.route('/campaign/unflag/<int:id>', methods=['POST'])
@login_required
@admin_required
def unflag_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    
    # Update the flag field
    campaign.flag = False
    db.session.commit()
    
    flash('The campaign has been unflagged!', 'success')
    return redirect(url_for('main.admin_info'))

@main.route('/user/flag/<int:id>', methods=['POST'])
@login_required
@admin_required
def flag_user(id):
    user = User.query.get_or_404(id)
    
    # Update the flag field
    user.flag = True
    db.session.commit()
    
    flash('The user has been flagged!', 'success')
    return redirect(url_for('main.admin_info'))

@main.route('/user/unflag/<int:id>', methods=['POST'])
@login_required
@admin_required
def unflag_user(id):
    user = User.query.get_or_404(id)
    
    # Update the flag field
    user.flag = False
    db.session.commit()
    
    flash('The user has been unflagged!', 'success')
    return redirect(url_for('main.admin_info'))

@main.route('/campaign/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_campaign(id):
    campaign = Campaign.query.get_or_404(id)

    # Check if the current user is the owner of the campaign
    if campaign.user_id != current_user.id:
        flash('You do not have permission to delete this campaign.', 'danger')
        return redirect(url_for('main.dashboard'))

    # Delete all ad requests associated with the campaign
    AdRequest.query.filter_by(campaign_id=id).delete()

    # Delete the campaign
    db.session.delete(campaign)
    db.session.commit()
    
    flash('Your campaign and all associated ad requests have been deleted!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/campaign/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    
    # Check if the current user is the owner of the campaign
    if campaign.user_id != current_user.id:
        flash('You do not have permission to edit this campaign.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if campaign.flag == True:
        flash('This Campaign is flagged')
        return redirect(url_for('main.dashboard'))

    form = CampaignForm(obj=campaign)
    
    if form.validate_on_submit():
        campaign.name = form.name.data
        campaign.description = form.description.data
        campaign.budget = form.budget.data
        campaign.visibility = form.visibility.data
        campaign.start_date = form.start_date.data
        campaign.end_date = form.end_date.data

        db.session.commit()
        flash('Your campaign has been edited!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('edit_campaign.html', title='Edit Campaign', form=form, campaign=campaign)

@main.route('/ad_request/new/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def new_ad_request(campaign_id):
    form = AdRequestForm()
    campaign = Campaign.query.get_or_404(campaign_id)

    if campaign.flag == True:
        flash('This Campaign is flagged')
        return redirect(url_for('main.dashboard'))

    # Fetch influencers and set choices for the SelectField
    influencers = [(influencer.id, influencer.username) for influencer in User.query.filter_by(role='influencer', flag=0).all()]
    form.influencer_id.choices = influencers

    if form.validate_on_submit():
        ad_request = AdRequest(
            requirements=form.requirements.data,
            influencer_id=form.influencer_id.data,
            payment_amount=form.payment_amount.data,
            campaign_id=campaign_id,
            status_sponsor='Accepted',
            status_influencer='Pending'
        )
        db.session.add(ad_request)
        db.session.commit()
        flash('Ad Request created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('create_ad_request.html', title='Create Ad Request', form=form, campaign_id=campaign_id)

@main.route('/ad_request_spon/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ad_request_spon(id):
    adrequest = AdRequest.query.get_or_404(id)
    campaign = Campaign.query.get_or_404(adrequest.campaign_id)

    if campaign.flag == True:
        flash('This Campaign is flagged')
        return redirect(url_for('main.dashboard'))
    
    # Check if the current user is the owner of the campaign
    if campaign.user_id != current_user.id:
        flash('You do not have permission to edit this ad request.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = AdRequestForm(obj=adrequest)
    
    influencers = [(influencer.id, influencer.username) for influencer in User.query.filter_by(role='influencer', flag=0).all()]
    form.influencer_id.choices = influencers

    if form.validate_on_submit():
        adrequest.influencer_id = form.influencer_id.data
        adrequest.requirements = form.requirements.data
        adrequest.payment_amount = form.payment_amount.data
        adrequest.status_sponsor = 'Accepted'
        adrequest.status_influencer = 'Pending'
        db.session.commit()
        flash('Your Ad Request has been edited!', 'success')
        return redirect(url_for('main.dashboard'))
    else:
        print(form.errors)  # Debug print for form errors
    
    return render_template('edit_ad_request_sponsor.html', title='Edit Ad Request', form=form, adrequest=adrequest)

@main.route('/new_ad_request/new/<int:campaign_id>/<int:influencer_id>', methods=['GET', 'POST'])
@login_required
def new_ad_request_infl(campaign_id, influencer_id):
    form = AdRequestForm()
    campaign = Campaign.query.get_or_404(campaign_id)

    if campaign.flag == True:
        flash('This Campaign is flagged')
        return redirect(url_for('main.dashboard'))

    # Set the influencer_id choices
    form.influencer_id.choices = [(influencer.id, influencer.username) for influencer in User.query.filter_by(role='influencer').all()]

    if request.method == 'POST':
        form.influencer_id.data = influencer_id

    if request.method == 'POST':
        form.influencer_id.data = influencer_id
    if form.validate_on_submit():
        ad_request = AdRequest(
            campaign_id=campaign_id,
            influencer_id=influencer_id,
            requirements=form.requirements.data,
            payment_amount=form.payment_amount.data,
            status_sponsor='Pending',
            status_influencer='Accepted'
        )
        db.session.add(ad_request)
        db.session.commit()
        flash('Your ad request has been created!', 'success')
        return redirect(url_for('main.influencer_profile'))
    return render_template('create_ad_request_influencer.html', title='Request New Ad', form=form, campaign_id=campaign_id, influencer_id=influencer_id)

@main.route('/ad_request_infl/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ad_request_infl(id):
    adrequest = AdRequest.query.get_or_404(id)
    campaign = Campaign.query.get_or_404(adrequest.campaign_id)
    # new_id=current_user.id
    # print(adrequest.influencer_id)
    if campaign.flag == True:
        flash('This Campaign is flagged')
        return redirect(url_for('main.dashboard'))
    
    # Check if the current user is the owner of the ad request
    if ((adrequest.influencer_id != current_user.id) and adrequest.influencer_id != 1):
        flash('You do not have permission to edit this ad request.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = AdRequestForm(obj=adrequest)

    influencers = [(influencer.id, influencer.username) for influencer in User.query.filter_by(role='influencer', flag=0).all()]
    form.influencer_id.choices = influencers
    
    if form.validate_on_submit():
        # The below will force influencer_id when it is set to public user
        adrequest.influencer_id = current_user.id
        adrequest.payment_amount = form.payment_amount.data
        adrequest.status_sponsor = 'Pending'
        adrequest.status_influencer = 'Accepted'
        db.session.commit()
        flash('Your Ad Request has been edited!', 'success')
        return redirect(url_for('main.dashboard'))
    else:
        print(form.errors)  # Debug print for form errors
    
    return render_template('edit_ad_request_influencer.html', title='Edit Ad Request', form=form, adrequest=adrequest)

@main.route('/ad_request/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_ad_request(id):
    ad_request = AdRequest.query.get_or_404(id)
    campaign = Campaign.query.get_or_404(ad_request.campaign_id)

    # Check if the current user is the owner of the campaign
    if campaign.user_id != current_user.id:
        flash('You do not have permission to edit this ad request.', 'danger')
        return redirect(url_for('main.dashboard'))

    if campaign.flag == True:
        flash('This Campaign is flagged')
        return redirect(url_for('main.dashboard'))
    
    # Delete the ad request
    db.session.delete(ad_request)
    db.session.commit()

    flash('Your ad request has been deleted!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/sponsor/profile')
@login_required
def sponsor_profile():
    if current_user.role != 'sponsor':
        return redirect(url_for('main.dashboard'))

    sponsor = current_user
    # active_campaigns = Campaign.query.filter_by(visibility='public').all()
    active_campaigns = Campaign.query.join(AdRequest, Campaign.id == AdRequest.campaign_id)\
    .filter(Campaign.user_id == sponsor.id, AdRequest.status_sponsor == "Accepted").all()
    new_requests = AdRequest.query.join(Campaign, AdRequest.campaign_id == Campaign.id)\
    .filter(
        Campaign.user_id == sponsor.id,
        AdRequest.status_sponsor == 'Pending', AdRequest.status_influencer != 'Rejected'
    ).all()
    active_influencer = User.query.filter_by(role='influencer').all()
    influencer_pending_request = AdRequest.query.join(Campaign, AdRequest.campaign_id == Campaign.id)\
                              .filter(Campaign.user_id == sponsor.id, AdRequest.status_influencer == 'Pending', AdRequest.status_sponsor != 'Rejected').all()

    return render_template('sponsor_profile.html',
                           sponsor=sponsor,
                           active_campaigns=active_campaigns,
                           active_influencer=active_influencer,
                           new_requests=new_requests,
                           influencer_pending_request=influencer_pending_request)

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
    return redirect(url_for('main.dashboard'))


@main.route('/sponsor/find')
@login_required
def sponsor_find():
    if current_user.role == 'sponsor':
        # active_influencer = User.query.filter_by(role='influencer').all()
        # # print(active_influencer)
        # return render_template('sponsor_find.html', sponsor=current_user, active_influencer=active_influencer)
        search_query = request.args.get('search', '')
        if search_query:
            # Perform search query on your users
            active_influencer = User.query.filter(User.role == 'influencer', or_(User.username.ilike(f"%{search_query}%"), User.platforms.ilike(f"%{search_query}%"), User.category.ilike(f"%{search_query}%"), User.niche.ilike(f"%{search_query}%"))).all()
        else:
            # Fetch all users if no search query
            active_influencer = User.query.filter_by(role='influencer').all()

        return render_template('sponsor_find.html', sponsor=current_user, active_influencer=active_influencer)
    return redirect(url_for('main.dashboard'))

@main.route('/influencer_details/<int:id>')
@login_required
def view_influencer(id):
    # Implement the logic to view campaign details
    influencer = User.query.get_or_404(id)
    print(id)
    return render_template('influencer_details.html', user=influencer)

@main.route('/sponsor_details/<int:id>')
@login_required
def view_sponsor(id):
    # Implement the logic to view campaign details
    sponsor = User.query.get_or_404(id)
    # print(id)
    return render_template('sponsor_details.html', user=sponsor)

@main.route('/admin_details/<int:id>')
@login_required
def view_admin(id):
    # Implement the logic to view campaign details
    admin = User.query.get_or_404(id)
    # print(id)
    return render_template('admin_details.html', user=admin)

@main.route('/sponsor/stats')
@login_required
def sponsor_stats():
    if current_user.role != 'sponsor':
        return redirect(url_for('main.dashboard'))

    campaigns = Campaign.query.filter_by(user_id=current_user.id).all()
    campaign_names = [campaign.name for campaign in campaigns]
    campaign_budgets = [campaign.budget for campaign in campaigns]

    return render_template('sponsor_stats.html',
                           campaign_names=campaign_names,
                           campaign_budgets=campaign_budgets)


# For Influencers
# @main.route('/influencer/profile')
# @login_required
# def influencer_profile():
#     if current_user.role == 'influencer':
#         return render_template('influencer_profile.html')
#     return redirect(url_for('main.home'))
@main.route('/influencer/profile')
@login_required
def influencer_profile():
    if current_user.role != 'influencer':
        return redirect(url_for('main.dashboard'))

    influencer = current_user
    print(current_user.id)
    public_influencer = User.query.filter_by(username='Public').first()
    # active_campaigns = Campaign.query.filter_by(visibility='public').all()
    active_campaigns = Campaign.query.join(AdRequest, Campaign.id == AdRequest.campaign_id) \
    # .filter(or_(
    #     and_(AdRequest.status_influencer == 'Accepted', AdRequest.influencer_id == current_user.id),
    #     and_(AdRequest.status_influencer == 'Pending', AdRequest.influencer_id == public_influencer.id)
    # )).all()
    # To show only accepted campaigns
    active_campaigns = Campaign.query.join(AdRequest, Campaign.id == AdRequest.campaign_id) \
    .filter(and_(AdRequest.status_influencer == 'Accepted', AdRequest.influencer_id == current_user.id)).all()
    print(active_campaigns)
    new_requests = AdRequest.query.filter(
        (AdRequest.influencer_id == public_influencer.id) | 
        (AdRequest.influencer_id == influencer.id),
        AdRequest.status_influencer == 'Pending',
        AdRequest.status_sponsor != 'Rejected'
    ).all()
    sponsor_pending_request = AdRequest.query.filter_by(influencer_id=influencer.id, status_sponsor='Pending').all()

    return render_template('influencer_profile.html',
                           influencer=influencer,
                           active_campaigns=active_campaigns,
                           new_requests=new_requests,
                           sponsor_pending_request=sponsor_pending_request)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@main.route('/update_profile_pic', methods=['POST'])
@login_required
def update_profile_pic():
    if 'profile_pic' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['profile_pic']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        # Generate a unique filename based on user ID
        filename = f"{current_user.id}_{uuid.uuid4().hex}.png"

        # Secure the filename
        filename = secure_filename(filename)

        # Define the path to save the new profile picture
        filepath = os.path.join(current_app.root_path, 'static/profile_pics', filename)

        # Delete the old profile picture if it's not the default one
        old_filepath = os.path.join(current_app.root_path, 'static/profile_pics', current_user.profile_pic)
        if os.path.exists(old_filepath) and current_user.profile_pic != 'download.png':
            os.remove(old_filepath)

        # Save the new profile picture
        file.save(filepath)

        # Update the user's profile picture filename in the database
        current_user.profile_pic = filename
        db.session.commit()

        flash('Your profile picture has been updated!', 'success')
        return redirect(url_for('main.influencer_profile'))

@main.route('/campaign_details/<int:campaign_id>', methods=['GET'])
@login_required
def campaign_details(campaign_id):
    print(campaign_id)
    campaign = Campaign.query.get_or_404(campaign_id)
    public_influencer = User.query.filter_by(username='Public').first()
    
    # # Ensure the user has permission to view this campaign
    # if campaign.user_id != current_user.id:
    #     abort(403)
    
    if current_user.role == "influencer":
        ads = AdRequest.query.filter(
            AdRequest.campaign_id == campaign.id,
            or_(
                AdRequest.influencer_id == current_user.id,
                AdRequest.influencer_id == public_influencer.id
            )
        ).all()
    elif current_user.role == "sponsor":
        ads = AdRequest.query.filter_by(campaign_id=campaign.id).all()
    
    elif current_user.role == "admin":
        ads = AdRequest.query.filter_by(campaign_id=campaign.id).all()
        # print(ads)
        
    return render_template('campaign_details.html', campaign=campaign, ads=ads)

@main.route('/ad_request_details/<int:ad_request_id>', methods=['GET'])
@login_required
def ad_request_details(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    return render_template('ad_request_details.html', ad_request=ad_request)

@main.route('/accept_request/<int:id>')
@login_required
def accept_request_influencer(id):
    # Implement the logic to accept ad request
    ad_request = AdRequest.query.get_or_404(id)
    ad_request.status_influencer = 'Accepted'
    db.session.commit()
    return redirect(url_for('main.influencer_profile'))

@main.route('/reject_request/<int:id>')
@login_required
def reject_request_influencer(id):
    # Implement the logic to reject ad request
    ad_request = AdRequest.query.get_or_404(id)
    ad_request.influencer_id = current_user.id
    ad_request.status_influencer = 'Rejected'
    db.session.commit()
    return redirect(url_for('main.influencer_profile'))

@main.route('/accept_request/s/<int:id>')
@login_required
def accept_request_sponsor(id):
    # Implement the logic to accept ad request
    ad_request = AdRequest.query.get_or_404(id)
    ad_request.status_sponsor = 'Accepted'
    db.session.commit()
    return redirect(url_for('main.sponsor_profile'))

@main.route('/reject_request/s/<int:id>')
@login_required
def reject_request_sponsor(id):
    # Implement the logic to reject ad request
    ad_request = AdRequest.query.get_or_404(id)
    ad_request.status_sponsor = 'Rejected'
    db.session.commit()
    return redirect(url_for('main.sponsor_profile'))

@main.route('/influencer/find')
@login_required
def influencer_find():
    if current_user.role == 'influencer':
        # influencer = current_user
        # active_campaigns = Campaign.query.filter_by(visibility='public').all()

        # return render_template('influencer_find.html', influencer=current_user, active_campaigns=active_campaigns)
        search_query = request.args.get('search', '')
        if search_query:
            active_campaigns = Campaign.query.filter(and_(Campaign.name.ilike(f'%{search_query}%'), Campaign.visibility=='public')).all()
        else:
            active_campaigns = Campaign.query.filter_by(visibility='public').all()
        
        return render_template('influencer_find.html', influencer=current_user, active_campaigns=active_campaigns)
    return redirect(url_for('main.dashboard'))

# @main.route('/influencer/stats')
# @login_required
# def influencer_stats():
#     if current_user.role != 'influencer':
#         return redirect(url_for('main.dashboard'))

#     # For demonstration purposes, we use dummy data
#     months = ['January', 'February', 'March', 'April', 'May', 'June']
#     earnings = [500, 700, 800, 600, 900, 1100]

#     return render_template('influencer_stats.html',
#                            months=months,
#                            earnings=earnings)

@main.route('/influencer/stats')
@login_required
def influencer_stats():
    if current_user.role != 'influencer':
        return redirect(url_for('main.dashboard'))

    # Query the database for the ad requests related to the current influencer
    ad_requests = AdRequest.query.filter_by(influencer_id=current_user.id).all()
    earnings_by_month = defaultdict(float)

    for ad_request in ad_requests:
        start_date = ad_request.campaign.start_date
        end_date = ad_request.campaign.end_date
        payment_amount = ad_request.payment_amount

        # Calculate the total number of days in the campaign
        total_days = (end_date - start_date).days + 1

        # Calculate the earnings per day
        daily_earning = payment_amount / total_days

        current_date = start_date
        while current_date <= end_date:
            month = current_date.strftime('%B')
            days_in_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1) - current_date.replace(day=1)
            month_days = min(days_in_month.days, (end_date - current_date).days + 1)
            
            earnings_by_month[month] += daily_earning * month_days
            current_date += timedelta(days=month_days)

    # Ensure we have data for all months
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    earnings = [earnings_by_month.get(month, 0) for month in months]

    return render_template('influencer_stats.html',
                           months=months,
                           earnings=earnings)

# For Admins
@main.route('/admin/info')
@login_required
def admin_info():
    if current_user.role == 'admin':
        users = User.query.all()
        campaigns = Campaign.query.all()
        ad_requests = AdRequest.query.all()
        return render_template('admin_info.html', users=users, campaigns=campaigns, ad_requests=ad_requests)
    return redirect(url_for('main.dashboard'))

@main.route('/admin/find')
@login_required
def admin_find():
    if current_user.role == 'admin':
        # users = User.query.all()
        campaigns = Campaign.query.all()
        ad_requests = AdRequest.query.all()
        search_query1 = request.args.get('search-user','')
        if search_query1:
            users = User.query.filter(
                or_(
                    User.username.ilike(f"%{search_query1}%"),
                    User.platforms.ilike(f"%{search_query1}%"),
                    User.role.ilike(f"%{search_query1}%"),
                    User.industry.ilike(f"%{search_query1}%"),
                    User.category.ilike(f"%{search_query1}%"),
                    User.niche.ilike(f"%{search_query1}%"),
                    User.flag.ilike(f"%{search_query1}%")
                )
            )
        else:
            users = User.query.all()

        search_query2 = request.args.get('search-campaign','')
        if search_query2:
            campaigns = Campaign.query.filter(
                or_(
                    Campaign.name.ilike(f'%{search_query2}%'),
                    Campaign.description.ilike(f'%{search_query2}%'),
                    Campaign.budget.ilike(f'%{search_query2}%'),
                    Campaign.visibility.ilike(f'%{search_query2}%'),
                    Campaign.start_date.ilike(f'%{search_query2}%'),
                    Campaign.end_date.ilike(f'%{search_query2}%'),
                    Campaign.flag.ilike(f'%{search_query2}%')
                )
            )
        else:
            campaigns = Campaign.query.all()
        
        search_query3 = request.args.get('search-adrequest','')
        if search_query3:
            ad_requests = AdRequest.query.filter(or_((AdRequest.requirements.ilike(f'%{search_query3}%')),(AdRequest.payment_amount.ilike(f'%{search_query3}%')),(AdRequest.status_influencer.ilike(f'%{search_query3}%')),(AdRequest.status_sponsor.ilike(f'%{search_query3}%'))))
        else:
            ad_requests = AdRequest.query.all()

        return render_template('admin_find.html', users=users, campaigns=campaigns, ad_requests=ad_requests)
    return redirect(url_for('main.dashboard'))

@main.route('/admin/stats')
@login_required
def admin_stats():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))

    sponsors_count = User.query.filter_by(role='sponsor').count()
    influencers_count = User.query.filter_by(role='influencer').count()
    user_counts = [sponsors_count, influencers_count]

    active_campaigns_count = Campaign.query.filter(Campaign.end_date >= date.today()).count()
    active_campaigns = [active_campaigns_count]

    ongoing_ad_requests_count = AdRequest.query.filter(AdRequest.status_sponsor=='Accepted', AdRequest.status_influencer=='Accepted').count()
    rejected_ad_requests_count = AdRequest.query.filter((AdRequest.status_sponsor=='Rejected') | (AdRequest.status_influencer=='Rejected')).count()
    ad_request_counts = [ongoing_ad_requests_count, rejected_ad_requests_count]

    flagged_users_count = User.query.filter_by(flag=True).count()
    flagged_campaigns_count = Campaign.query.filter_by(flag=True).count()
    flagged_counts = [flagged_users_count, flagged_campaigns_count]

    return render_template('admin_stats.html',
                           user_counts=user_counts,
                           active_campaigns=active_campaigns,
                           ad_request_counts=ad_request_counts,
                           flagged_counts=flagged_counts)
