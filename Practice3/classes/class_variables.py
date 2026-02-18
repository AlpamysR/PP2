class Dog:
    # Class variable - shared by all instances
    species = "Canis familiaris"
    total_dogs = 0
    
    def __init__(self, name, age):
        # Instance variables - unique to each instance
        self.name = name
        self.age = age
        
        # Modify the class variable
        Dog.total_dogs += 1

# Creating instances
dog1 = Dog("Buddy", 3)
dog2 = Dog("Max", 5)

# Accessing class variable through the class
print(Dog.species)  # "Canis familiaris"
print(Dog.total_dogs)  # 2

# Accessing class variable through instances (also works)
print(dog1.species)  # "Canis familiaris"
print(dog2.species)  # "Canis familiaris"