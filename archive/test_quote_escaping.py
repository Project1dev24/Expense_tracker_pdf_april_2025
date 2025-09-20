"""
Test quote escaping for the onclick attribute
"""

def test_quote_escaping():
    """Test different approaches to quote escaping"""
    
    # Test names
    test_names = ["taylor", "test user", "test'user"]
    
    print("Testing different quote escaping approaches:")
    
    for name in test_names:
        print(f"\nName: {repr(name)}")
        
        # Approach 1: Double quotes with tojson (problematic)
        approach1 = f'onclick="setParticipantName({repr(name)});"'
        print(f"Approach 1 (double quotes + repr): {approach1}")
        
        # Approach 2: Single quotes with tojson (better)
        approach2 = f"onclick='setParticipantName({repr(name)});'"
        print(f"Approach 2 (single quotes + repr): {approach2}")
        
        # Approach 3: Double quotes with JSON (problematic)
        import json
        json_name = json.dumps(name)
        approach3 = f'onclick="setParticipantName({json_name});"'
        print(f"Approach 3 (double quotes + JSON): {approach3}")
        
        # Approach 4: Single quotes with JSON (better)
        approach4 = f"onclick='setParticipantName({json_name});'"
        print(f"Approach 4 (single quotes + JSON): {approach4}")

if __name__ == "__main__":
    test_quote_escaping()