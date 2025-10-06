miles = [1.1, 0.8, 2.5, 2.6]               
fares = ("$6.25", "$5.25", "$10.50", "$8.05") # tuple (fixed/immutable)

trips = {"miles": miles, "fares": fares}
print(trips)

print(f"3rd trip: {trips['miles'][2]} miles, {trips['fares'][2]}")

