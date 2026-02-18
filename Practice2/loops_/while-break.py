#Breaking while loop
i = 1
while i < 6:
  print(i)
  if i == 3:
    break       #Breaking there and while loop stopping
  i += 1

#Breaking when user entering "quit"
while True:
    user_input = input("Enter something (or 'quit' to exit): ")
    if user_input == 'quit':
        print("Exiting loop.")
        break  # Terminates the while loop
    print(f"You entered: {user_input}")
    
print("Program finished.")

#Breaking when number is 3
i = 1
while i < 6:
  print(i)
  if i == 3:
    print("Breaking the loop at 3")
    break  # Exit the loop immediately
  i += 1