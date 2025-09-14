# Group Members
members = ["You", "Bob", "Charlie", "David", "Emma"]

# Expenses
expenses = [
    {"paid_by": "You", "amount": 6000.00, "split_between": members},               # Hotel
    {"paid_by": "Bob", "amount": 1200.00, "split_between": members},               # Groceries
    {"paid_by": "Charlie", "amount": 2000.00, "split_between": members},           # Fuel
    {"paid_by": "Emma", "amount": 1500.00, "split_between": members},              # Entry Tickets
    {"paid_by": "David", "amount": 2500.00, "split_between": ["You", "Bob", "David"]},  # Dinner
]

# Advance payments from outside contributors (Alex & Nina)
advances = {
    "Emma": 2000.00,   # Paid by Alex on Bob's behalf
    "David": 1000.00,  # Paid by Nina on Emma's behalf
}

# Initialize balances
balances = {member: 0.0 for member in members}

# Process expenses
for expense in expenses:
    payer = expense["paid_by"]
    amount = expense["amount"]
    split_between = expense["split_between"]
    share = amount / len(split_between)

    balances[payer] += amount
    for person in split_between:
        balances[person] -= share

# Apply advances
for person, advance in advances.items():
    balances[person] -= advance

# Round balances
balances = {person: round(balance, 2) for person, balance in balances.items()}

# Identify who owes and who is owed
owed = {p: amt for p, amt in balances.items() if amt > 0}
owes = {p: -amt for p, amt in balances.items() if amt < 0}

# Generate settlements
settlements = []
for debtor, debt_amt in owes.items():
    for creditor, credit_amt in owed.items():
        if credit_amt == 0:
            continue
        payment = min(debt_amt, credit_amt)
        if payment > 0:
            settlements.append((debtor, creditor, round(payment, 2)))
            owes[debtor] -= payment
            owed[creditor] -= payment
            debt_amt -= payment
            if owes[debtor] <= 0:
                break

# Output results
print("💰 Net Balances (after expenses & advances):")
for person, balance in balances.items():
    status = "is owed" if balance > 0 else "owes"
    print(f"{person}: {status} ₹{abs(balance):.2f}")

print("\n📋 Suggested Settlements:")
for debtor, creditor, amount in settlements:
    print(f"{debtor} pays {creditor} ₹{amount:.2f}")
