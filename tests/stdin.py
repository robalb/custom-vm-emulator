
stdin = "a" * 2
requested = 4

read = 0
ret = ""
for i in range(min(requested, len(stdin))):
    read = i+1
    ret += stdin[i]
    
print(read, ret)





