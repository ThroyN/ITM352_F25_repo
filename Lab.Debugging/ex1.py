product = {
    "name": 'small gumball',
    "price": 0.34  # numeric, not a string
}

tax_rate = 0.045

# calculate total with tax
total = product["price"] + (product["price"] * tax_rate)

print(f"A {product['name']} costs ${total:.2f}")
