#Continue statement
fruits = ["apple", "banana", "cherry"]
for x in fruits:
  if x == "banana":
    continue
  print(x)
  
#Skipping iteration
for i in range(6):
  if i == 3:
    continue  # Skip the rest of the loop body for the current iteration
  print(f"Number: {i}")
  
#Ignoring elements
for letter in 'geeksforgeeks':
  if letter == 'e' or letter == 's':
    continue  # Skip printing 'e' and 's'
  print(f'Current Letter: {letter}')
