# Manual calculation of balances for trip 16

# Participants
participants = ["Alex", "Bob", "Charlie", "David", "Emma"]

# Expenses with payer, amount, and participants
expenses = [
    {"paid_by": "Charlie", "amount": 9500.00, "description": "festival", "participants": ["Alex", "Bob", "Charlie", "David", "Emma"]},
    {"paid_by": "Emma", "amount": 4200.00, "description": "campstie", "participants": ["Alex", "Bob", "Charlie", "David", "Emma"]},
    {"paid_by": "Alex", "amount": 3600.00, "description": "fuel", "participants": ["Alex", "Bob", "Charlie", "David", "Emma"]},
    {"paid_by": "Bob", "amount": 1950.00, "description": "grocieses", "participants": ["Alex", "Bob", "Charlie", "David", "Emma"]},
    {"paid_by": "David", "amount": 1200.00, "description": "tent", "participants": ["Charlie", "David", "Alex"]},
    {"paid_by": "Charlie", "amount": 1600.00, "description": "brush", "participants": ["Alex", "Bob", "Charlie", "David", "Emma"]},
]

# Advances
advances = {
    "Emma": 1000.00,
    "Bob": 3000.00,
}

# Initialize balances
balances = {participant: 0.0 for participant in participants}

print("Initial balances:", balances)

# Process each expense
for expense in expenses:
    payer = expense["paid_by"]
    amount = expense["amount"]
    description = expense["description"]
    expense_participants = expense["participants"]
    
    # Add to payer's balance (they paid this amount)
    balances[payer] += amount
    print(f"After {description} paid by {payer} ({amount}): {balances}")
    
    # Subtract share from each participant
    share = amount / len(expense_participants)
    for person in expense_participants:
        balances[person] -= share
    print(f"After splitting {description} ({amount}) among {len(expense_participants)} people: {balances}")

# Subtract advances from balances (they already paid this money)
print("\nProcessing advances:")
for person, advance_amount in advances.items():
    balances[person] -= advance_amount
    print(f"After {person} advance ({advance_amount}): {balances}")

# Round balances
balances = {person: round(balance, 2) for person, balance in balances.items()}

print("\nFinal balances:")
for person, balance in balances.items():
    status = "is owed" if balance > 0 else "owes"
    print(f"{person}: {status} ₹{abs(balance):.2f}")

# Expected from the debug output:
# Alex: owes ₹970.00
# Bob: owes ₹5220.00
# Charlie: is owed ₹6530.00
# David: owes ₹3370.00
# Emma: owes ₹970.00