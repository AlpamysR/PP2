import os
import shutil
from functools import reduce

# 3. Use enumerate() and zip() for paired iteration
fruits  = ["apple", "banana", "cherry"]
prices  = [1.20, 0.50, 3.00]

print("\n✅ 3. enumerate() — indexed list:")
for i, fruit in enumerate(fruits, start=1):
    print(f"     [{i}] {fruit}")

print("\n     zip() — paired iteration:")
for fruit, price in zip(fruits, prices):
    print(f"     {fruit:<10} → ${price:.2f}")
    
# 4. Demonstrate type checking and conversions
mixed = [42, "hello", 3.14, True, None, [1, 2]]

for item in mixed:
    print(f"     {str(item):<12} → type: {type(item).__name__:<10}"
          f"  is int? {isinstance(item, int)}")

print("\n   Type conversions:")
print(f"     int('99')     → {int('99')!r}  ({type(int('99')).__name__})")
print(f"     float('3.14') → {float('3.14')!r}  ({type(float('3.14')).__name__})")
print(f"     str(2025)     → {str(2025)!r}  ({type(str(2025)).__name__})")
print(f"     bool(0)       → {bool(0)!r} ({type(bool(0)).__name__})")
print(f"     list((1,2,3)) → {list((1,2,3))!r}  ({type(list((1,2,3))).__name__})")