x = 3
y = "Hello, World!"
myvar = "John"
my_var = "John"
_my_var = "John"
myVar = "John"
MYVAR = "John"
myvar2 = "John"
x = str(3)    # x will be '3'
y = int(3)    # y will be 3
z = float(3)  # z will be 3.0

x, y, z = "Orange", "Banana", "Cherry"
print(x)
print(y)
print(z)

fruits = ["apple", "banana", "cherry"]
x, y, z = fruits
print(x)
print(y)
print(z)

x = "Python "
y = "is "
z = "awesome"
print(x + y + z)    #or use ,

#GLOBAL 
x = "awesome"
def myfunc():
  print("Python is " + x)
myfunc()

global a
