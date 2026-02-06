#Basic function of printing string
def my_function():
  print("Hello from a function")

my_function()

#Example of using functions
def fahrenheit_to_celsius(fahrenheit):
  return (fahrenheit - 32) * 5 / 9

print(fahrenheit_to_celsius(77))
print(fahrenheit_to_celsius(95))
print(fahrenheit_to_celsius(50))

#Putting function in variable
def get_greeting():
  return "Hello from a function"

message = get_greeting()
print(message)

#Creating space func
def my_function():
  pass
