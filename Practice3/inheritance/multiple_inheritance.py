class Flyer:
    def fly(self):
        return "Flying in the sky"

class Swimmer:
    def swim(self):
        return "Swimming in water"

# Multiple inheritance - inherits from both Flyer and Swimmer
class Duck(Flyer, Swimmer):
    def quack(self):
        return "Quack quack!"

duck = Duck()
print(duck.fly())    # "Flying in the sky"
print(duck.swim())   # "Swimming in water"
print(duck.quack())  # "Quack quack!"

#Hybrid cars
class Vehicle:
    def __init__(self, brand):
        self.brand = brand
    
    def start(self):
        return f"{self.brand} vehicle starting"

class Electric:
    def charge(self):
        return "Charging battery"

class Gas:
    def refuel(self):
        return "Refueling tank"

# Multiple inheritance with method overriding
class HybridCar(Vehicle, Electric, Gas):
    def __init__(self, brand, model):
        super().__init__(brand)
        self.model = model
    
    # Override the start method
    def start(self):
        parent_start = super().start()
        return f"{parent_start} in hybrid mode ({self.model})"

car = HybridCar("Toyota", "Prius")
print(car.start())    # "Toyota vehicle starting in hybrid mode (Prius)"
print(car.charge())   # "Charging battery"
print(car.refuel())   # "Refueling tank"
