import config

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
    print('------Statistics------')
    for level in config.levels:
        print("Level " + str(level) + ': ' + str(lines_count[level]) + ' : ' + str(dump_count[level]))