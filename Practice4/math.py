#Task 1

import math

def degrees_to_radians(degrees):
    """Convert degrees to radians"""
    return degrees * (math.pi / 180)

# Get input from user
degrees = float(input("Input degree: "))

# Calculate radians
radians = degrees_to_radians(degrees)

# Print result (formatting to match the example)
print(f"Output radian: {radians:.6f}")

#Task 2

def trapezoid_area(height, base1, base2):
    """Calculate area of a trapezoid: A = ((a + b) / 2) * h"""
    return ((base1 + base2) / 2) * height

# Get input from user
height = float(input("Height: "))
base1 = float(input("Base, first value: "))
base2 = float(input("Base, second value: "))

# Calculate area
area = trapezoid_area(height, base1, base2)

# Print result
print(f"Expected Output: {area}")

#Task 3

def regular_polygon_area(n_sides, side_length):
    """Calculate area of a regular polygon: A = (n * s²) / (4 * tan(π/n))"""
    return (n_sides * side_length ** 2) / (4 * math.tan(math.pi / n_sides))

# Get input from user
n_sides = int(input("Input number of sides: "))
side_length = float(input("Input the length of a side: "))

# Calculate area
area = regular_polygon_area(n_sides, side_length)

# Print result
print(f"The area of the polygon is: {int(area) if area.is_integer() else area}")

#Task 4

def parallelogram_area(base, height):
    """Calculate area of a parallelogram: A = base * height"""
    return base * height

# Get input from user
base = float(input("Length of base: "))
height = float(input("Height of parallelogram: "))

# Calculate area
area = parallelogram_area(base, height)

# Print result
print(f"Expected Output: {area}")

