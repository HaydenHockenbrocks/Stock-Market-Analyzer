def calculate(base, rate, years):
    total = base * (1 + rate) ** years
    return total

print (calculate(10000, 0.07, 10))
print (calculate(10000, 0.05, 10))
print (calculate(10000, 0.09, 10))