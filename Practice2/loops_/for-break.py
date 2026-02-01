#Breaking for loop
fruits = ["apple", "banana", "cherry"]
for x in fruits:
  print(x)
  if x == "banana":
    break      #Stopping loop when element is banana

#Disturbing when its 3
numbers = [1, 2, 3, 4, 5]
for num in numbers:
    if num == 3:
        print("Break condition met! Exiting the loop.")
        break  # Exit the loop immediately
    print(f"Current number: {num}")

print("Loop ended.")

#By every character in string
for letter in 'Python':
    if letter == 'h':
        print("Encountered 'h', breaking the loop.")
        break  # Exit the loop
    print(f"Current letter: {letter}")

print("Good bye!")
