def greet(name):
    print("Hello " + name)

def add(a, b):
    return a + b

def is_adult(age):
    if age >= 18:
        return True
    else:
        return False

greet("Sonic")
greet("Harish")

result = add(5, 3)
print("5 + 3 = " + str(result))

print(is_adult(20))
print(is_adult(15))

