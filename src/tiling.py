import src.geometry as geometry
import src.utils.progress as progress

import math

# todo move to config
unique_tiles = {
    1:set()
}

class TileId:
    x:int
    y:int
    def __eq__(self, another):
        return hasattr(another, 'x') and hasattr(another, 'y') and self.x == another.x and self.y == another.y
    def __hash__(self):
        return hash(str(self.x) + ':' + str(self.y))
    def ToString(self):
        return str(self.x) + ':' + str(self.y)

class TileIdGenerator:
    level:int
    tiles_count:int
    tile_height_in_degrees:float
    tile_width_in_degrees:float

    def __init__(self, level):
        self.level = level
        # todo think one more time if tile height in degrees must be the same
        self.tiles_count = math.pow(2,level)
        self.tile_height_in_degrees = 180 / self.tiles_count
        self.tile_width_in_degrees = self.tile_height_in_degrees

    def deg2num(self, coordinate:geometry.Coordinate, level):
        # math.floor()
        lat_rad = math.radians(coordinate.latitude)
        n = math.pow(2, level)
        xtile = int(((coordinate.longitude + 180.0) / 360.0) * n)
        ytile = int(((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0) * n)
        return (xtile, ytile)

    def getTileId(self, coordinate:geometry.Coordinate) -> TileId:
        id = TileId()
        # tile_coord = self.deg2num(coordinate, self.level)
        id.x = int((coordinate.longitude + 180) / self.tile_width_in_degrees)
        id.y = int((coordinate.latitude + 90) / self.tile_height_in_degrees)
        # id.x = tile_coord[0]
        # id.y = tile_coord[1]
        # ch = geometry.Coordinate(41.85, -87.65)
        # ch_tile = self.deg2num(ch, self.level)
        # print(ch_tile[0], ch_tile[1], self.level)
        # print(str(tile_coord[0]), str(tile_coord[1]), id.x, id.y)
        return id

    def tile2lon(self, x:int, z:int):
        return x / math.pow(2.0, z) * 360.0 - 180

    def tile2lat(self, y:int, z:int):
        # n = math.pow(2, z)
        n = math.pi - (2.0 * math.pi * y) / math.pow(2.0, z)
        return math.degrees(math.atan(math.sinh(n)))

    def getBoundingBox(self, tileId:TileId):
        bbox = geometry.BoundingBox()
        bbox.ne.latitude  = self.tile_height_in_degrees *  tileId.y    - 90
        bbox.ne.longitude = self.tile_width_in_degrees  * (tileId.x+1) - 180
        bbox.sw.latitude  = self.tile_height_in_degrees * (tileId.y+1) - 90
        bbox.sw.longitude = self.tile_width_in_degrees  *  tileId.x    - 180

        # bbox.ne.latitude  = self.tile2lat(tileId.y,   self.level)
        # bbox.ne.longitude = self.tile2lon(tileId.x+1, self.level)
        # bbox.sw.latitude  = self.tile2lat(tileId.y+1, self.level)
        # bbox.sw.longitude = self.tile2lon(tileId.x,   self.level)
        # print(str(bbox.ne.latitude) + ',' + str(bbox.ne.longitude), str(bbox.sw.latitude) + ',' + str(bbox.sw.longitude))
        return bbox

class Tile:
    bbox:geometry.BoundingBox
    id:TileId

    def __init__(self, coordinate:geometry.Coordinate, level:int):
        tileIdGenerator = TileIdGenerator(level)
        self.id = tileIdGenerator.getTileId(coordinate)
        self.bbox = tileIdGenerator.getBoundingBox(self.id)

def DistanceBetweenCoordinates(coord1:geometry.Coordinate, coord2:geometry.Coordinate):
    R = 6378137; # metres

    s = math.pi / 180
    
    φ1 = coord1.latitude * s # φ, λ in radians
    φ2 = coord2.latitude * s

    Δφ = (coord2.latitude-coord1.latitude) * s
    Δλ = (coord2.longitude-coord1.longitude) * s

    a = math.sin(Δφ/2) * math.sin(Δφ/2) + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ/2) * math.sin(Δλ/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c # in metres

def DetermineAffectedTiles(parsed_coordinates, tile_level):
    print("Distribute coordinates among BBoxes they occupy on zoom level(" + str(tile_level) + ")...", end=' ')
    tiles = dict()
    generator = TileIdGenerator(tile_level)
    for coord in parsed_coordinates:
        tile_id = generator.getTileId(coordinate=coord)
        if tile_id in tiles.keys():
            tiles[tile_id].append(coord)
        else:
            tiles[tile_id] = [coord]

    print(str(len(tiles.keys())) + " tiles")
    return tiles

def DetermineAffectedTiles2(parsed_lines, tile_level):
    # prog = progress.Progress("Distribute lines by tiles on level " + str(tile_level))
    tiles = dict()
    generator = TileIdGenerator(tile_level)

    total_lines_count = len(parsed_lines)
    for index, line in enumerate(parsed_lines):
        # prog.update(int(index / total_lines_count * 100))

        tile_id = generator.getTileId(coordinate=line.coordinate_from)
        if tile_level in unique_tiles.keys():
            unique_tiles[tile_level].add(tile_id)
        else:
            unique_tiles[tile_level] = set()
            unique_tiles[tile_level].add(tile_id)
        if tile_id in tiles.keys():
            tiles[tile_id].append(line)
        else:
            tiles[tile_id] = [line]

    # prog.update(100)
    # prog.finish()
    # print(str(tile_level) + ':' + str(len(tiles.keys())) + " tiles")
    return tiles