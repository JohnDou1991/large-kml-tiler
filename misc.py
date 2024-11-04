import filters
import stats
import tiling

def filter(parsed_lines, tile_level):
    result = []
    filter = filters.tile_level[tile_level]
    # filter = frc_filters[tile_level]
    for line in parsed_lines:
        if not filter is None:
            distance = tiling.DistanceBetweenCoordinates(line.coordinate_from, line.coordinate_to)
            if not filter[0] is None:
                if distance > filter[0]:
                    if not filter[1] is None:
                        if distance < filter[1]:
                            result.append(line)
                    else:
                        result.append(line)
            elif not filter[1] is None:
                if distance < filter[1]:
                    result.append(line)
        else:
            result.append(line)
    #     if not filter is None and tiling.DistanceBetweenCoordinates(line.coordinate_from, line.coordinate_to) < filter:
        # if not line.description is None:
        #     pos = line.description.find('frc:')
        #     frc = int(line.description[pos+5:pos+6])
        #     if frc > filter:
    #             continue
    #     else:
    #         result.append(line)
    return result
def level(line):
    distance = tiling.DistanceBetweenCoordinates(line.coordinate_from, line.coordinate_to)
    for level in filters.tile_level.keys():
        filter = filters.tile_level[level]
        if filter[0] is None:
            if filter[1] is None:
                return level
            elif distance < filter[1]:
                return level
        else:
            if distance > filter[0]:
                if filter[1] is None:
                    return level
                elif distance < filter[1]:
                    return level
        #             if distance < filter[1]:
        #         return level
        # else:
        #     if not filter[1] is None:
        #         if distance < filter[1]:
        #             return level
        #     else:
        #         return level

        # if not filter is None:
        #     if not filter[0] is None:
        #         if distance > filter[0]:
        #             if not filter[1] is None:
        #                 if distance < filter[1]:
        #                     result.append(line)
        #             else:
        #                 result.append(line)
        #     elif not filter[1] is None:
        #         if distance < filter[1]:
        #             result.append(line)
        # else:
            # result.append(line)

def distribute(lines):
    result = {
        13:[],
        11:[],
        9:[],
        7:[],
        5:[],
        3:[],
        1:[]
    }
    for line in lines:
        lvl = level(line)
        stats.lines_count[lvl] = stats.lines_count[lvl] + 1
        result[lvl].append(line)
    return result