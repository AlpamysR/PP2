import re

# 1. Match a string that has 'a' followed by zero or more 'b's
def exercise_1(text):
    return re.findall(r'ab*', text)

# 2. Match a string that has 'a' followed by two to three 'b's
def exercise_2(text):
    return re.findall(r'ab{2,3}', text)

# 3. Find sequences of lowercase letters joined with an underscore
def exercise_3(text):
    return re.findall(r'[a-z]+_[a-z]+', text)

# 4. Find sequences of one uppercase letter followed by lowercase letters
def exercise_4(text):
    return re.findall(r'[A-Z][a-z]+', text)

# 5. Match a string that has 'a' followed by anything, ending in 'b'
def exercise_5(text):
    return re.findall(r'a.*b', text)

# 6. Replace all occurrences of space, comma, or dot with a colon
def exercise_6(text):
    return re.sub(r'[ ,.]', ':', text)

# 7. Convert snake_case string to camelCase
def exercise_7(text):
    components = text.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

# 8. Split a string at uppercase letters
def exercise_8(text):
    return re.split(r'(?=[A-Z])', text)

# 9. Insert spaces between words starting with capital letters
def exercise_9(text):
    return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)

# 10. Convert camelCase string to snake_case
def exercise_10(text):
    s = re.sub(r'(?<=[a-z])(?=[A-Z])', '_', text)
    return s.lower()
    
  sep = '-' * 55

  print(sep)
  print("Exercise 1 – 'a' followed by zero or more 'b's")
  samples = ['ac', 'abc', 'abbc', 'abbbc', 'a', 'aab']
  for s in samples:
  print(f"  '{s}' → {exercise_1(s)}")

  print(sep)
  print("Exercise 2 – 'a' followed by two to three 'b's")
  samples = ['ab', 'abb', 'abbb', 'abbbb', 'abbc']
  for s in samples:
        print(f"  '{s}' → {exercise_2(s)}")

  print(sep)
    print("Exercise 3 – lowercase sequences joined with underscore")
    samples = ['hello_world', 'foo_bar_baz', 'Python_Code', 'abc_def', 'test']
    for s in samples:
        print(f"  '{s}' → {exercise_3(s)}")

  print(sep)
    print("Exercise 4 – one uppercase letter followed by lowercase letters")
    samples = ['Hello World', 'CamelCase', 'Python3', 'UPPER lower Mixed']
    for s in samples:
        print(f"  '{s}' → {exercise_4(s)}")

  print(sep)
    print("Exercise 5 – 'a' followed by anything, ending in 'b'")
    samples = ['aab', 'a123b', 'axyzb', 'ab', 'abc', 'ba']
    for s in samples:
        print(f"  '{s}' → {exercise_5(s)}")

  print(sep)
    print("Exercise 6 – replace space, comma, dot with colon")
    samples = ['Hello World', 'one,two,three', 'a.b.c', 'foo, bar. baz']
    for s in samples:
        print(f"  '{s}' → '{exercise_6(s)}'")

  print(sep)
  print("Exercise 7 – snake_case to camelCase")
  samples = ['hello_world', 'foo_bar_baz', 'my_variable_name']
  for s in samples:
        print(f"  '{s}' → '{exercise_7(s)}'")

  print(sep)
  print("Exercise 8 – split at uppercase letters")
  samples = ['CamelCaseString', 'HelloWorld', 'MyVariableName']
  for s in samples:
        result = [x for x in exercise_8(s) if x]  # remove empty strings
        print(f"  '{s}' → {result}")

  print(sep)
  print("Exercise 9 – insert spaces before capital letters")
  samples = ['CamelCaseString', 'HelloWorld', 'MyVariableName']
  for s in samples:
        print(f"  '{s}' → '{exercise_9(s)}'")

  print(sep)
  print("Exercise 10 – camelCase to snake_case")
  samples = ['camelCase', 'myVariableName', 'HelloWorld']
  for s in samples:
        print(f"  '{s}' → '{exercise_10(s)}'")

  print(sep)
