document.addEventListener('DOMContentLoaded', function() {
    // Function to handle opening the campaign modal
    function openCampaignModal(campaignId) {
        // Ensure the campaignId is not undefined
        if (!campaignId) {
            console.error('Campaign ID is undefined');
            return;
        }

        // Hide the ad request modal
        $('#adRequestModal').modal('hide');

        // Open the campaign modal after the ad request modal is hidden
        $('#adRequestModal').on('hidden.bs.modal', function () {
            var modal = $('#campaignModal');
            modal.find('.modal-body').load('/campaign_details/' + campaignId);
            modal.modal('show');
            // Unbind this event to prevent multiple triggers
            $(this).off('hidden.bs.modal');
        });
    }

    // Handle showing the campaign modal
    $('#campaignModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var campaignId = button.data('id');

        // Ensure the campaignId is not undefined
        if (!campaignId) {
            console.error('Campaign ID is undefined');
            return;
        }

        // Load the campaign details
        var modal = $(this);
        modal.find('.modal-body').load('/campaign_details/' + campaignId);
    });

    // Handle showing the ad request modal
    $('#adRequestModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var adRequestId = button.data('id');

        // Load the ad request details
        var modal = $(this);
        modal.find('.modal-body').load('/ad_request_details/' + adRequestId);

        // Hide the campaign modal
        $('#campaignModal').modal('hide');

        // If there's a campaign link in the ad request modal, bind the click event
        modal.on('click', '.campaign-link', function(event) {
            event.preventDefault();
            var campaignId = $(this).data('id');
            openCampaignModal(campaignId);
        });
    });

    // Ensure to hide modals if they are already open when opening another one
    $('#campaignModal').on('hidden.bs.modal', function () {
        if ($('.modal.show').length) {
            $('body').addClass('modal-open');
        }
    });

    $('#adRequestModal').on('hidden.bs.modal', function () {
        if ($('.modal.show').length) {
            $('body').addClass('modal-open');
        }
    });

    $('#influencerModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var influencerId = button.data('id');

        var modal = $(this);
        modal.find('.modal-body').load('/influencer_details/' + influencerId);
    });

    $('#sponsorModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var sponsorId = button.data('id');

        var modal = $(this);
        modal.find('.modal-body').load('/sponsor_details/' + sponsorId);
    });

    $('#adminModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var adminId = button.data('id');

        var modal = $(this);
        modal.find('.modal-body').load('/admin_details/' + adminId);
    });
});

document.querySelector('.scrollable-container').addEventListener('scroll', function() {
    const container = this;
    const cardHeight = container.querySelector('.col-md-4').offsetHeight;
    const scrollPosition = container.scrollTop;
    const rowHeight = cardHeight + parseInt(getComputedStyle(container.querySelector('.col-md-4')).marginBottom, 10);

    // Adjust scrolling behavior to align to rows
    if (scrollPosition % rowHeight !== 0) {
        container.scrollTop = Math.round(scrollPosition / rowHeight) * rowHeight;
    }
});

// Event listener for buttons
document.querySelectorAll('.btn[data-target]').forEach(button => {
    button.addEventListener('click', function() {
        const userId = this.getAttribute('data-id');
        const modalTarget = this.getAttribute('data-target');
        
        // Determine the appropriate URL to load based on modalTarget
        let detailsUrl = '';
        // Check if these match your backend routes and modal IDs
        if (modalTarget === '#influencerModal') {
            detailsUrl = `/influencer_details/${userId}`;
        } else if (modalTarget === '#adminModal') {
            detailsUrl = `/admin_details/${userId}`;
        } else if (modalTarget === '#sponsorModal') {
            detailsUrl = `/sponsor_details/${userId}`;
        }
        
        if (userId) {
            loadModal(modalTarget, detailsUrl);
        }
    });
});