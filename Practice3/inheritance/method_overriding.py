#Overriding methods
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        return f"{self.name} makes a sound"
    
    def move(self):
        return f"{self.name} moves"

class Dog(Animal):
    # Overriding the speak method
    def speak(self):
        return f"{self.name} barks"

class Cat(Animal):
    # Overriding the speak method
    def speak(self):
        return f"{self.name} meows"
    
    # Overriding the move method
    def move(self):
        return f"{self.name} prowls silently"

# Using the classes
dog = Dog("Buddy")
cat = Cat("Whiskers")

print(dog.speak())  # "Buddy barks"
print(cat.speak())  # "Whiskers meows"
print(cat.move())   # "Whiskers prowls silently"
