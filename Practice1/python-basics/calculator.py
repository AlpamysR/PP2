def calc(num1, num2, operation):
    if operation == '+':
        return num1 + num2
    elif operation == '-':
        return num1 - num2
    elif operation == '*':
        return num1 * num2
    elif operation == '/':
        if num2 == 0:
            return "Error: Division by zero is not allowed."
        return num1 / num2
    else:
        return "Error: Invalid operation entered."


print("Welcome to the simple calculator!")

number1 = float(input("Enter the first number: "))
number2 = float(input("Enter the second number: "))
op = input("Enter the operation (+, -, *, /): ")

result = calc(number1, number2, op)
print(f"The result is: {result}")