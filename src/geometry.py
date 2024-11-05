class Coordinate:
    latitude:float
    longitude:float

    def __init__(self):
        pass

    # parameterized constructor
    def __init__(self, lat, lon):
        self.latitude = lat
        self.longitude = lon

class Line:
    coordinate_from:Coordinate
    coordinate_to:Coordinate
    description:str
    name:str
    style:str
    when:str

    # parameterized constructor
    def __init__(self, coord_from, coord_to):
        self.coordinate_from = coord_from
        self.coordinate_to = coord_to

class BoundingBox:
    sw:Coordinate
    ne:Coordinate

    def __init__(self):
        self.sw = Coordinate(None, None)
        self.ne = Coordinate(None, None)
    
    def toString(self) -> str:
        sw_dump = "SW: " + str(self.sw.latitude) + ',' + str(self.sw.longitude)
        ne_dump = " NE: " + str(self.ne.latitude) + ',' + str(self.ne.longitude)
        return sw_dump + ne_dump

def CalculateOverallBBox(coordinates):
    print("Calculate overall bbox...")
    overall_bbox = BoundingBox()
    for coordinate in coordinates:
        if overall_bbox.sw.latitude is None or overall_bbox.sw.latitude < coordinate.latitude:
            overall_bbox.sw.latitude = coordinate.latitude
        if overall_bbox.sw.longitude is None or overall_bbox.sw.longitude < coordinate.longitude:
            overall_bbox.sw.longitude = coordinate.longitude
        if overall_bbox.ne.latitude is None or overall_bbox.ne.latitude > coordinate.latitude:
            overall_bbox.ne.latitude = coordinate.latitude
        if overall_bbox.ne.longitude is None or overall_bbox.ne.longitude > coordinate.longitude:
            overall_bbox.ne.longitude = coordinate.longitude
    print("Overall bounding box: " + overall_bbox.toString())