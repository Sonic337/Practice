class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        print(f"Hi, I'm {self.name} and I'm {self.age} years old")

    def is_adult(self):
        return self.age >= 18

class Employee(Person):
    def __init__(self, name, age, role):
        super().__init__(name, age)
        self.role = role

    def introduce(self):
        print(f"I'm {self.name}, {self.role} at the company")

sonic = Person("Sonic", 20)
sonic.greet()
print(sonic.is_adult())

harish = Employee("Harish", 35, "CEO")
harish.greet()
harish.introduce()

