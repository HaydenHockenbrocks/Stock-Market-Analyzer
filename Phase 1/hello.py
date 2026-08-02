#This Program says hello and asks for your name and age, then responds with a message.

print('hello World!')
print('what is your name?')
name = input()
print('hello ' + name + '! Nice to meet you!')
print('Your name is ' + str(len(name)) + ' characters long.')
print('What is your age?')
age = input()
print('You will be ' + str(int(age) + 1) + ' years old next year!')


