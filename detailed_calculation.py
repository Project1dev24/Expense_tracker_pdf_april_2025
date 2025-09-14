# Detailed calculation to verify balances

# Participants and their IDs from database
# Alex (22), Bob (27), Charlie (28), David (30), Emma (29)

# Expenses with actual data from database
expenses = [
    {"id": 94, "description": "festival", "paid_by": "Charlie", "amount": 9500.00, "participants": ["Alex", "Bob", "Charlie", "David", "Emma"]},
    {"id": 95, "description": "campstie", "paid_by": "Emma", "amount": 4200.00, "participants": ["Alex", "Bob", "Charlie", "David", "Emma"]},
    {"id": 96, "description": "fuel", "paid_by": "Alex", "amount": 3600.00, "participants": ["Alex", "Bob", "Charlie", "David", "Emma"]},
    {"id": 97, "description": "grocieses", "paid_by": "Bob", "amount": 1950.00, "participants": ["Alex", "Bob", "Charlie", "David", "Emma"]},
    {"id": 98, "description": "tent", "paid_by": "David", "amount": 1200.00, "participants": ["Charlie", "David", "Alex"]},
    {"id": 99, "description": "brush", "paid_by": "Charlie", "amount": 1600.00, "participants": ["Alex", "Bob", "Charlie", "David", "Emma"]},
]

# Advances from database
advances = {
    "Emma": 1000.00,
    "Bob": 3000.00,
}

# Initialize tracking
total_paid = {"Alex": 0.0, "Bob": 0.0, "Charlie": 0.0, "David": 0.0, "Emma": 0.0}
total_share = {"Alex": 0.0, "Bob": 0.0, "Charlie": 0.0, "David": 0.0, "Emma": 0.0}

print("=== Expense Breakdown ===")
for expense in expenses:
    payer = expense["paid_by"]
    amount = expense["amount"]
    participants = expense["participants"]
    
    # Add to payer's total paid
    total_paid[payer] += amount
    print(f"\n{expense['description']} (₹{amount}) paid by {payer}")
    print(f"  {payer} paid: +₹{amount}")
    
    # Calculate share per participant
    share = amount / len(participants)
    print(f"  Split among {len(participants)} people: ₹{share} each")
    
    # Add to each participant's share
    for person in participants:
        total_share[person] += share
        print(f"  {person}'s share: +₹{share}")

print("\n=== Advances ===")
for person, amount in advances.items():
    total_paid[person] += amount
    print(f"{person} paid advance: +₹{amount}")

print("\n=== Totals ===")
balances = {}
for person in total_paid.keys():
    balance = total_paid[person] - total_share[person]
    balances[person] = balance
    print(f"{person}:")
    print(f"  Total Paid: ₹{total_paid[person]}")
    print(f"  Total Share: ₹{total_share[person]}")
    print(f"  Balance: ₹{balance} ({'owes' if balance < 0 else 'is owed' if balance > 0 else 'settled'})")

print("\n=== Final Balances ===")
for person, balance in balances.items():
    status = "is owed" if balance > 0 else "owes" if balance < 0 else "settled"
    amount = abs(balance) if balance != 0 else 0
    print(f"{person}: {status} ₹{amount:.2f}")

# Verify the settlement status table data
print("\n=== Verification Against Settlement Status Table ===")
settlement_table = {
    "bob": {"paid": 4950.0, "share": 4170.0, "status": "bob should receive ₹780.0"},
    "charlie": {"paid": 11100.0, "share": 4570.0, "status": "charlie should receive ₹6530.0"},
    "david": {"paid": 1200.0, "share": 4570.0, "status": "david should give ₹3370.0"},
    "emma": {"paid": 5200.0, "share": 4170.0, "status": "emma should receive ₹1030.0"},
    "Alex": {"paid": 3600.0, "share": 4570.0, "status": "Alex should give ₹970.0"}
}

print("Checking if our calculations match the settlement table:")
for person, data in settlement_table.items():
    # Convert person name to match our calculation (lowercase first letter for Bob, Charlie, David, Emma)
    calc_person = person
    if person == "bob":
        calc_person = "Bob"
    elif person == "charlie":
        calc_person = "Charlie"
    elif person == "david":
        calc_person = "David"
    elif person == "emma":
        calc_person = "Emma"
    
    our_paid = total_paid[calc_person]
    our_share = total_share[calc_person]
    our_balance = balances[calc_person]
    
    print(f"\n{person}:")
    print(f"  Table - Paid: ₹{data['paid']}, Share: ₹{data['share']}")
    print(f"  Ours  - Paid: ₹{our_paid}, Share: ₹{our_share}")
    print(f"  Match: {data['paid'] == our_paid and data['share'] == our_share}")
    print(f"  Balance: ₹{our_balance} ({'owes' if our_balance < 0 else 'is owed' if our_balance > 0 else 'settled'})")
    print(f"  Status: {data['status']}")