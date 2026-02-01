#Using elif as the next if
a = 33
b = 33
if b > a:
  print("b is greater than a")
elif a == b:
  print("a and b are equal") # <-Output

#Multiple elif clause
score = 75
if score >= 90:
  print("Grade: A")
elif score >= 80:
  print("Grade: B")
elif score >= 70:
  print("Grade: C") # <-Output
elif score >= 60:
  print("Grade: D")
  
#Only the first true condition will be executed.
#Even if multiple conditions are true,
#Python stops after executing the first matching block.

age = 25
if age < 13:
  print("You are a child")
elif age < 20:
  print("You are a teenager")
elif age < 65:
  print("You are an adult") # <-Output
elif age >= 65:
  print("You are a senior")
