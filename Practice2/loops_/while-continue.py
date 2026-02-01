#Using continue to pass a number
i = 0
while i < 6:
  i += 1
  if i == 3:
    continue  #Pass a step
  print(i)

#Printing odd numbers
num = 0
while num < 10:
    num += 1  # Increment first to avoid an infinite loop if the condition is met immediately
    if (num % 2) == 0:
        continue  # Skip the print statement for even numbers
    print(num)

#Skipping specific items
animals = ['dog', 'cat', 'pig', 'horse', 'cow']
index = 0
while index < len(animals):
    if animals[index] == 'dog':
        index += 1  # Crucial: Must increment the index before continuing
        continue    # Skip printing 'dog'
    
    print(animals[index])
    index += 1
