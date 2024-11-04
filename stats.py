lines_count = {
    13:0,
    11:0,
    9:0,
    7:0,
    5:0,
    3:0,
    1:0
}

dump_count = {
    13:0,
    11:0,
    9:0,
    7:0,
    5:0,
    3:0,
    1:0
}

def dump():
    print("Statistics: ")
    indx = 13
    while indx > 0:
        print("Level " + str(indx) + ': ' + str(lines_count[indx]) + ' : ' + str(dump_count[indx]))
        indx = indx - 2