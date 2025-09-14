"""
Test how the template renders the onclick attribute with different names
"""

from flask import Flask, render_template_string

# Create a simple Flask app for testing
app = Flask(__name__)

def test_template_rendering():
    """Test how the template renders with different names"""
    
    # Test template
    template = '''
    <button type="button" class="dropdown-item" data-bs-toggle="modal" data-bs-target="#linkModal" onclick="setParticipantName({{ name|tojson }});">
        Link to User
    </button>
    '''
    
    # Test with different names
    test_names = [
        "taylor",
        "shivram",
        "jordan",
        "test user",
        "test'user",  # Name with apostrophe
        "",  # Empty string
    ]
    
    with app.app_context():
        print("Testing template rendering with different names:")
        for name in test_names:
            rendered = render_template_string(template, name=name)
            print(f"Name: {repr(name)}")
            print(f"Rendered: {rendered.strip()}")
            print()

if __name__ == "__main__":
    test_template_rendering()