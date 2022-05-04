import random

def generate_matrix():
    row = int(input('How many rows?:'))
    column = int(input('How many columns?:'))
    y = 0
    list = []
    new_list = []
    for i in range(row*column):
        list.append(i)
    random.shuffle(list)

    for i in range(row):
        x = []
        for j in range(column):
            x.append(list[y])
            y += 1
        new_list.append(x)
    return list
print(generate_matrix())