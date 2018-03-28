def printall(text,num = 0,pluss = 3):
    typ = type(text)
    if str(typ) == "<class 'dict'>":
        for key,value in text.items():
            if str(type(value)) == "<class 'dict'>" or str(type(value)) == "<class 'list'>":
                printall(value,num = num+pluss)
            else:
                print("-" * num, key, ":",value)
    elif str(typ) == "<class 'list'>":
        for item in text:
            if str(type(item)) == "<class 'dict'>" or str(type(item)) == "<class 'list'>":
                printall(item,num = num+pluss)
            else:
                print("-" * num, item)
    else:
        print("-" * num, text)