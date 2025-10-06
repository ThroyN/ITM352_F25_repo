responses = [5, 7, 3, 8]


responses = responses + [0]


responses = responses[:2] + [6] + responses[2:]


print(responses)
