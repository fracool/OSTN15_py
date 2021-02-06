from math import cos, tan, sin, radians


def get_line(line, lines):
    """Read the data from the line in the lines object."""
    my_line = lines[line]
    line_list = my_line.split(',')
    ns, es, ys = line_list[3], line_list[4], line_list[5]
    return float(ns), float(es), float(ys)


class Shift:
    """Perform the shifts to get corrections to apply to our eastings & northings."""
    def __init__(self, north, east):
        with open('data.txt', 'r') as data:
            lines = data.readlines()
            self.north = int(north / 1000)
            self.east = int(east / 1000)
            self.s0 = get_line(self.east + (701 * self.north) + 1, lines)
            print(self.s0)
            self.s1 = get_line(self.east + 1 + (701 * self.north) + 1, lines)
            print(self.s1)
            self.s2 = get_line(self.east + 1 + (701 * (self.north + 1)) + 1, lines)
            print(self.s2)
            self.s3 = get_line(self.east + (701 * (self.north + 1)) + 1, lines)
            print(self.s3)
            self.dx = north - self.north * 1000
            self.dy = east - self.east * 1000
            self.t = self.dx / 1000
            self.u = self.dy / 1000


def gps_to_os(lat, lng):
    """Convert GRS80 to OSGM15."""
    # Setting up our constants provided to us in the OSTN15 Resource
    A = 6378137.0000  # GRS80 Semi Major Axis
    B = 6356752.3141  # GRS80 Semi Minor Axis
    A2 = pow(A, 2)
    B2 = pow(B, 2)

    # Ellipsoid squared constant
    E2 = (A2 - B2) / A2
    print("E2 is {}".format(E2))

    # Scale factor on central meridian
    FO = 0.9996012717

    # True origin
    LNGO = radians(-2)
    LATO = radians(49)

    # True origin map coords (m)
    EO = 400000
    NO = -100000

    GPS_LON = radians(lng)  # radians(1.716073972)
    GPS_LAT = radians(lat)  # radians(52.658007833)

    n = (A - B) / (A + B)
    n2 = pow(n, 2)
    n3 = pow(n, 3)

    sinLat = sin(GPS_LAT)
    cosLat = cos(GPS_LAT)
    tanLat = tan(GPS_LAT)
    cos3Lat = pow(cosLat, 3)
    cos5Lat = pow(cosLat, 5)
    tan2Lat = pow(tanLat, 2)
    tan4Lat = pow(tanLat, 4)
    sin2Lat = pow(sinLat, 2)

    v = A * FO * pow(1 - E2 * sin2Lat, -0.5)
    print("V is {}".format(v))

    p = A * FO * (1 - E2) * pow((1 - E2 * sin2Lat), -1.5)
    print("P is ", end='')
    print(p)

    funnyN = (v / p) - 1
    print("funnyN is ", end='')
    print(funnyN)

    m1 = (1 + n + (5 / 4) * n2 + (5 / 4) * n3) * (GPS_LAT - LATO)
    m2 = (3 * n + 3 * n2 + (21 / 8) * n3) * sin(GPS_LAT - LATO) * cos(GPS_LAT + LATO)
    m3 = ((15 / 8) * n2 + (15 / 8) * n3) * sin(2 * (GPS_LAT - LATO)) * cos(2 * (GPS_LAT + LATO))
    m4 = (35 / 24) * n3 * sin(3 * (GPS_LAT - LATO)) * cos(3 * (GPS_LAT + LATO))
    M = B * FO * (m1 - m2 + m3 - m4)

    print("Big one... M is ", end='')
    print(M)

    I = M + NO
    print("I: ", end='')
    print(I)

    II = (v / 2) * sinLat * cosLat
    print("II: ", end='')
    print(II)

    III = (v / 24) * sinLat * cos3Lat * (5 - tan2Lat + 9 * funnyN)
    print("III: ", end='')
    print(III)

    IIIA = (v / 720) * sinLat * cos5Lat * (61 - 58 * tan2Lat + tan4Lat)
    print("IIIA: ", end='')
    print(IIIA)

    IV = v * cosLat
    print("IV: ", end='')
    print(IV)

    V = (v / 6) * cos3Lat * ((v / p) - tan2Lat)
    print("V: ", end='')
    print(V)

    VI = (v / 120) * cos5Lat * (5 - 18 * tan2Lat + tan4Lat + 14 * funnyN - 58 * funnyN * tan2Lat)
    print("VI: ", end='')
    print(VI)

    NORTH = I + II * pow((GPS_LON - LNGO), 2) + III * pow((GPS_LON - LNGO), 4) + IIIA * pow((GPS_LON - LNGO), 6)
    EAST = EO + IV * (GPS_LON - LNGO) + V * pow((GPS_LON - LNGO), 3) + VI * pow((GPS_LON - LNGO), 5)

    # Now we still have to apply shifts, stored in the OSTN15 data file
    print("Northing: ", end='')
    print(NORTH, end='')
    print(" Easting: ", end='')
    print(EAST)

    sh = Shift(NORTH, EAST)  # Calculate shifts for each corner of the grid tile

    se = (1 - sh.t) * (1 - sh.u) * sh.s0[0] + sh.t * (1 - sh.u) * sh.s1[0] + sh.t * sh.u * sh.s2[0] + (
                1 - sh.t) * sh.u * sh.s3[0]
    sn = (1 - sh.t) * (1 - sh.u) * sh.s0[1] + sh.t * (1 - sh.u) * sh.s1[1] + sh.t * sh.u * sh.s2[1] + (
                1 - sh.t) * sh.u * sh.s0[1]

    e = EAST + se
    n = NORTH + sn

    print("Corrected East: ", end='')
    print(e, end='')
    print(" North: ", end='')
    print(n, end='')
    return e, n

# EXAMPLE USE
# INPUT_LAT = 50.178909
# INPUT_LNG = 0.22556677


# gps_to_os(INPUT_LAT, INPUT_LNG)


# while True:
    # print("\nOSGM15 with mm accuracy. Select q to quit.")
    # usr_lat, usr_lng = input("enter Latitude and Longitude separated by a comma: ").split(',')
    # if usr_lat == 'q':
    #     break
    # gps_to_os(float(usr_lat), float(usr_lng))
