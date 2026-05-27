# write to a file
with open("output.txt", "w") as f:
    f.write("Hello from Python\n")
    f.write("This is a second line\n")

# read from a file
with open("output.txt", "r") as f:
    content = f.read()
    print(content)

# append to a file
with open("output.txt", "a") as f:
    f.write("This line was appended\n")

# read line by line
with open("output.txt", "r") as f:
    for line in f:
        print(line.strip())
