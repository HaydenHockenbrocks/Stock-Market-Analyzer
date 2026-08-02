base = 1
returns = 0.07
years = 10

total = base * (1 + returns) ** years
print(f'Your total money after {years} years is: ${total:.2f}')

if total > 20000:
    print('Congratulations! Your investment was good!')
elif total > 15000:
    print('Not bad, but you could have done better.')
else :
    print ('Unfortunately, your investment did not perform well.')