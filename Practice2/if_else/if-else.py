#If-elif-else clause
a = 200
b = 33
if b > a:
  print("b is greater than a")
elif a == b:
  print("a and b are equal")
else:
  print("a is greater than b") # <-Output , only happens if nothing fits
  
#Without elif
a = 200
b = 33
if b > a:
  print("b is greater than a")
else:
  print("b is not greater than a") # <-Output
  
#Note: The else statement must come last. You cannot have an elif after an else.

#Else as Fallback
username = "Emil"
if len(username) > 0:
  print(f"Welcome, {username}!")
else:
  print("Error: Username cannot be empty")
