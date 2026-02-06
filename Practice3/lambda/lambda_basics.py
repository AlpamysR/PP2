#Syntax 
#lambda arguments : expression

#Basic lambda
x = lambda a : a + 10
print(x(5))

#Multiple arguments
x = lambda a, b : a * b
print(x(5, 6))

#Lambda in function
def myfunc(n):
  return lambda a : a * n

mytripler = myfunc(3)

print(mytripler(11))
