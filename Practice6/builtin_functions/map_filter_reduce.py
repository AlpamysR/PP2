import os
import shutil
from functools import reduce

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# 1. Use map() and filter() on lists
squared = list(map(lambda x: x ** 2, numbers))
evens   = list(filter(lambda x: x % 2 == 0, numbers))

print(f"\n 1. Original list : {numbers}")
print(f"     map()  squares: {squared}")
print(f"     filter()  evens: {evens}")

# 2. Aggregate with reduce() (from functools)
total   = reduce(lambda acc, x: acc + x, numbers)
product = reduce(lambda acc, x: acc * x, numbers)

print(f"\n 2. reduce() sum of list     : {total}")
print(f"     reduce() product of list : {product}")
