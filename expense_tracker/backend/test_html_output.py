"""
Test what the actual HTML output looks like for the manage participants page
"""

from app import app
from backend.models.trip import Trip
from backend.models.user import User
from flask import render_template

def test_html_output():
    """Test the HTML output of the manage participants template"""
    with app.app_context():
        # Get a trip
        trip = Trip.query.first()
        if not trip:
            print("No trips found")
            return
            
        print(f"Testing with trip: {trip.name} (ID: {trip.id})")
        
        # Get participants data like the route does
        participant_ids = trip.get_participants_list()
        participants = User.query.filter(User.id.in_([int(pid) for pid in participant_ids if pid.isdigit()])).all()
        
        # Get all registered users for linking (including admin if not already in participants)
        all_registered_users = participants.copy()
        admin_user = User.query.get(trip.admin_id)
        if admin_user and admin_user not in all_registered_users:
            all_registered_users.append(admin_user)
        
        # Get unregistered participants (use display names)
        unregistered_participants = trip.get_unregistered_participants_display()
        
        print(f"Unregistered participants: {unregistered_participants}")
        
        # Render the template with sample data
        # Let's test with a simple name first
        test_unregistered = ["taylor", "test user"]
        
        # Render the template
        html = render_template('trips/manage_participants.html', 
                              trip=trip,
                              participants=participants,
                              unregistered_participants=test_unregistered,
                              all_registered_users=all_registered_users)
        
        # Look for the onclick attribute in the HTML
        import re
        onclick_matches = re.findall(r'onclick="([^"]*)"', html)
        print(f"Found {len(onclick_matches)} onclick attributes:")
        for i, match in enumerate(onclick_matches):
            print(f"  {i+1}. {match}")

if __name__ == "__main__":
    test_html_output()