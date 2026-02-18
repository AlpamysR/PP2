#Task 1

def square_generator(n):
    """Generator that yields squares of numbers from 0 to n"""
    for i in range(n + 1):
        yield i ** 2

# Test the generator
print("Task 1: Squares up to 10")
for square in square_generator(10):
    print(square, end=" ")
print("\n")

#Task 2

def even_numbers_generator(n):
    """Generator that yields even numbers from 0 to n"""
    for i in range(n + 1):
        if i % 2 == 0:
            yield i

# Get input from console
n = int(input("Task 2: Enter a number n: "))

# Collect even numbers and print in comma-separated form
even_numbers = list(even_numbers_generator(n))
print(f"Even numbers from 0 to {n}:")
print(", ".join(map(str, even_numbers)))
print()

#Task 3

def divisible_by_3_and_4_generator(n):
    """Generator that yields numbers divisible by both 3 and 4 (i.e., divisible by 12)"""
    for i in range(n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

# Test the generator
n = int(input("Task 3: Enter a number n: "))
print(f"Numbers divisible by both 3 and 4 from 0 to {n}:")
for num in divisible_by_3_and_4_generator(n):
    print(num, end=" ")
print("\n")

#Task 4

def squares(a, b):
    """Generator that yields squares of numbers from a to b"""
    for i in range(a, b + 1):
        yield i ** 2

# Test with a for loop
print("Task 4: Squares from 5 to 10")
a, b = 5, 10
for square in squares(a, b):
    print(f"{square}", end=" ")
print("\n")

# Additional test with different range
print("Additional test: Squares from 1 to 5")
for square in squares(1, 5):
    print(f"{square}", end=" ")
print("\n")

#Task 5

def countdown_generator(n):
    """Generator that yields numbers from n down to 0"""
    for i in range(n, -1, -1):
        yield i

# Test the generator
n = int(input("Task 5: Enter a number n: "))
print(f"Numbers from {n} down to 0:")
for num in countdown_generator(n):
    print(num, end=" ")
print()