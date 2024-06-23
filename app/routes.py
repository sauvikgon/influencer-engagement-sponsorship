from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.models import User, Campaign, AdRequest
# from app.forms import RegistrationForm, LoginForm, CampaignForm, AdRequestForm
from app.forms import SponsorRegistrationForm, InfluencerRegistrationForm, LoginForm, CampaignForm, AdRequestForm
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os

main = Blueprint('main', __name__)

# # We have commented this because this was showing home page we need to show loginpage
# @main.route('/')
# @main.route('/home')
# def home():
#     return render_template('home.html')

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
        campaign = Campaign(name=form.name.data, description=form.description.data, budget=form.budget.data, visibility=form.visibility.data, start_date=form.start_date.data, end_date=form.end_date.data, user_id=current_user.id)
        db.session.add(campaign)
        db.session.commit()
        flash('Your campaign has been created!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('create_campaign.html', title='New Campaign', form=form)

@main.route('/campaign/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    
    # Check if the current user is the owner of the campaign
    if campaign.user_id != current_user.id:
        flash('You do not have permission to edit this campaign.', 'danger')
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
    
     # Fetch influencers and set choices for the SelectField
    influencers = [(influencer.id, influencer.username) for influencer in User.query.filter_by(role='influencer').all()]
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
    
    # Check if the current user is the owner of the campaign
    if campaign.user_id != current_user.id:
        flash('You do not have permission to edit this ad request.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = AdRequestForm(obj=adrequest)
    
    if form.validate_on_submit():
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
    
    # Check if the current user is the owner of the ad request
    if adrequest.influencer_id != current_user.id:
        flash('You do not have permission to edit this ad request.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = AdRequestForm(obj=adrequest)
    
    if form.validate_on_submit():
        # adrequest.influencer_id = form.influencer_id.data
        adrequest.payment_amount = form.payment_amount.data
        adrequest.status_sponsor = 'Pending'
        adrequest.status_influencer = 'Accepted'
        db.session.commit()
        flash('Your Ad Request has been edited!', 'success')
        return redirect(url_for('main.dashboard'))
    else:
        print(form.errors)  # Debug print for form errors
    
    return render_template('edit_ad_request_influencer.html', title='Edit Ad Request', form=form, adrequest=adrequest)

@main.route('/sponsor/profile')
@login_required
def sponsor_profile():
    if current_user.role != 'sponsor':
        return redirect(url_for('main.home'))

    sponsor = current_user
    # active_campaigns = Campaign.query.filter_by(visibility='public').all()
    active_campaigns = Campaign.query.join(AdRequest, Campaign.id == AdRequest.campaign_id)\
    .filter(Campaign.user_id == sponsor.id, AdRequest.status_sponsor == "Accepted").all()
    new_requests = AdRequest.query.join(Campaign, AdRequest.campaign_id == Campaign.id)\
                              .filter(Campaign.user_id == sponsor.id, AdRequest.status_sponsor == 'Pending').all()
    influencer_pending_request = AdRequest.query.join(Campaign, AdRequest.campaign_id == Campaign.id)\
                              .filter(Campaign.user_id == sponsor.id, AdRequest.status_influencer == 'Pending').all()

    return render_template('sponsor_profile.html',
                           sponsor=sponsor,
                           active_campaigns=active_campaigns,
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
    return redirect(url_for('main.home'))


@main.route('/sponsor/find')
@login_required
def sponsor_find():
    if current_user.role == 'sponsor':
        active_influencer = User.query.filter_by(role='influencer').all()
        # print(active_influencer)
        return render_template('sponsor_find.html', sponsor=current_user, active_influencer=active_influencer)
    return redirect(url_for('main.home'))

@main.route('/influencer_details/<int:id>')
@login_required
def view_influencer(id):
    # Implement the logic to view campaign details
    influencer = User.query.get_or_404(id)
    # print(id)
    return render_template('influencer_details.html', user=influencer)

@main.route('/sponsor/stats')
@login_required
def sponsor_stats():
    if current_user.role == 'sponsor':
        # You may need to add logic to gather relevant stats
        return render_template('sponsor_stats.html')
    return redirect(url_for('main.home'))


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
        return redirect(url_for('main.home'))

    influencer = current_user
    # active_campaigns = Campaign.query.filter_by(visibility='public').all()
    active_campaigns = Campaign.query.join(AdRequest, Campaign.id == AdRequest.campaign_id)\
    .filter(AdRequest.status_influencer == 'Accepted', AdRequest.influencer_id == influencer.id).all()
    public_influencer = User.query.filter_by(username='Public').first()
    new_requests = AdRequest.query.filter(
        (AdRequest.influencer_id == public_influencer.id) | 
        (AdRequest.influencer_id == influencer.id),
        AdRequest.status_influencer == 'Pending'
    ).all()
    sponsor_pending_request = AdRequest.query.filter_by(influencer_id=influencer.id, status_sponsor='Pending').all()

    return render_template('influencer_profile.html',
                           influencer=influencer,
                           active_campaigns=active_campaigns,
                           new_requests=new_requests,
                           sponsor_pending_request=sponsor_pending_request)

@main.route('/update_profile_pic', methods=['POST'])
def update_profile_pic():
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            # Update user's profile picture path in the database
            current_user.profile_pic = filename
            db.session.commit()
    return redirect(url_for('main.influencer_profile'))

@main.route('/campaign_details/<int:campaign_id>', methods=['GET'])
@login_required
def campaign_details(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # # Ensure the user has permission to view this campaign
    # if campaign.user_id != current_user.id:
    #     abort(403)
    
    if current_user.role == "influencer":
        ads = AdRequest.query.filter_by(campaign_id=campaign.id, influencer_id = current_user.id).all()
    elif current_user.role == "sponsor":
        ads = AdRequest.query.filter_by(campaign_id=campaign.id).all()
    return render_template('campaign_details.html', campaign=campaign, ads=ads)


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
        influencer = current_user
        active_campaigns = Campaign.query.filter_by(visibility='public').all()

        return render_template('influencer_find.html', influencer=current_user, active_campaigns=active_campaigns)
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
