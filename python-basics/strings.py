print("Hello")
print('Hello')  #SAME
a = """Lorem ipsum dolor sit amet,
consectetur adipiscing elit,
sed do eiusmod tempor incididunt
ut labore et dolore magna aliqua."""
print(a)   #SAME

a = "Hello, World!"
print(a[1])  #WILL GIVE LETTER e

for x in "banana":
  print(x) #WILL GIVE EVERY LETTER

len(a) #COUNT OF LETTERs

txt = "The best things in life are free!"
if "free" in txt:
  print("Yes, 'free' is present.")
  
b = "Hello, World!"
print(b[2:5]) 
#llo
print(b[:5]) 
#Hello
print(b[2:])
#llo, World!
print(b[-5:-2])
#orl

a = "Hello, World!"
print(a.upper())
print(a.lower())

a = " Hello, World! "
print(a.strip()) # returns "Hello, World!"

a = "Hello, World!"
print(a.replace("H", "J"))

a = "Hello, World!"
print(a.split(",")) # returns ['Hello', ' World!']

a = "Hello"
b = "World"
c = a + " " + b
print(c)

age = 36
txt = f"My name is John, I am {age}"
print(txt)

price = 59
txt = f"The price is {price:.2f} dollars" #2 decimal numbers after
print(txt)

txt = "We are the so-called \" Vikings \" from the north." #We are the so-called "Vikings" from the north.

