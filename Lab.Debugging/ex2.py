prices = [5.95, 3.00, 12.50]
total_price = 0
tax_rate = 1.08    # 8% tax included as multiplier

for price in prices:
    total_price += price * tax_rate   # add each item's total with tax

print(f"Total price (with tax): ${total_price:.2f}")
