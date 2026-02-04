#Basic While loop
i = 1
while i < 6:
  print(i)
  i += 1

#Counting up something
count = 0 
while count < 5:  
    print(count)  
    count += 1

#Username loop
user_input = ""
while user_input != "quit":
    user_input = input("Enter 'quit' to exit: ")
    print(f"You entered: {user_input}")

print("Loop terminated.")
    
    
