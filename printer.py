import math
import matplotlib.pyplot as plt

degrees_to_radians = math.pi / 180
radians_to_degrees = 180 / math.pi

def get_xy(alpha, beta):

    r = 3  # short arm length (attached to the rotative axis)
    a = 8  # long arm length
    b = a  # distance from short arm extremity to pen
    s = 0  # pen distance

    xa = -5 #left short arm x
    xb = 5 #right short arm x

    # d is the first short arm extremity
    xd = xa - r * math.sin(alpha)
    yd = r * math.cos(alpha)

    # e is the first short arm extremity
    xe = xb - r * math.sin(beta)
    ye = r * math.cos(beta)

    de = compute_distance(xd, yd, xe, ye)

    #theta is the angle formed by de and the left long arm
    cos_theta = de/float(2 * a)
    cos_theta = min(cos_theta, 1.0)
    cos_theta = max(cos_theta, -1.0)
    theta = math.acos(cos_theta)


    #gamma is the angle formed by an horizontal axis and de
    #gamma = math.acos(math.pow(xd-xe, 2)/float(math.pow(xd-xe, 2) + math.pow(yd-ye, 2)))
    #gamma = math.copysign(gamma, ye-yd)

    tan_gamma = (ye-yd)/float(xe-xd)
    gamma = math.atan(tan_gamma)
    #print gamma * radians_to_degrees, gamma2 * radians_to_degrees


    #lambda is the angle formed by an horizontal axis and the left long arm
    lam = theta + gamma
    xt = xd + b * math.cos(lam) - s * math.sin(lam)
    yt = yd + b * math.sin(lam) + s * math.cos(lam)

    return xt, yt

class StructureSetting:
    def __init__(self):
        self.r = 3  # short arm length (attached to the rotative axis)
        self.a = 8  # long arm length
        self.b = self.a  # distance from short arm extremity to pen
        self.s = 1  # pen distance

        self.xa = -5 #left short arm x
        self.xb = 5 #right short arm x

def compute_circle_intersection(x0, y0, x1, y1, r0, r1):
    d = compute_distance(x0, y0, x1, y1)
    if d < math.fabs(r0 - r1) or r0 +r1 < d:
        return None

    a = (math.pow(r0, 2) - math.pow(r1, 2) + math.pow(d, 2))/float(2 * d)
    h = math.sqrt(math.pow(r0, 2) - math.pow(a, 2))

    x2 = x0 + a * (x1 - x0)/float(d)
    y2 = y0 + a * (y1 - y0)/float(d)

    x3 = x2 + h * (y1 - y0)/ d
    y3 = y2 - h * (x1 - x0)/ d

    x3_prime = x2 - h * (y1 - y0)/ d
    y3_prime = y2 + h * (x1 - x0)/ d
    print "intersections", (x3, y3), (x3_prime, y3_prime)
    return (x3, y3), (x3_prime, y3_prime)



def get_alpha_beta(x, y, structure_settings):
    intersection1 = compute_circle_intersection(structure_settings.xa, 0, x, y, structure_settings.r, structure_settings.a)
    if intersection1 is None:
        return None
    (x1, y1), (x1_prime, y1_prime) = intersection1
    alpha = math.atan2(structure_settings.xa - x1, y1) * radians_to_degrees
    alpha_prime = math.atan2(structure_settings.xa - x1_prime, y1_prime) * radians_to_degrees

    if x1 < x1_prime:
        alpha_result = alpha
    else:
        alpha_result = alpha_prime

    intersection2 = compute_circle_intersection(structure_settings.xb, 0, x, y, structure_settings.r, structure_settings.a)
    if intersection2 is None:
        return None
    (x2, y2), (x2_prime, y2_prime) = intersection2

    beta = math.atan2(structure_settings.xb - x2, y2) * radians_to_degrees
    beta_prime = math.atan2(structure_settings.xb - x2_prime, y2_prime) * radians_to_degrees

    if x2 > x2_prime:
        beta_result = beta
    else:
        beta_result = beta_prime

    return alpha_result, beta_result


def change_referential(x, y):
    angle = 0 * degrees_to_radians
    return (x * math.cos(angle)  + y * math.sin(angle), -x * math.sin(angle) + y * math.cos(angle))

def get_closest_grid_point(x, y, points_per_lego_unit = 2):
    x_grid = round(x * points_per_lego_unit) / float(points_per_lego_unit)
    y_grid = round(y * points_per_lego_unit) / float(points_per_lego_unit)
    return x_grid, y_grid

def compute_distance(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2-x1, 2) + math.pow(y2-y1, 2))

def spirograph(nb_loops, beta_coefficient):
    xs=[]
    ys=[]
    for alpha_degrees in range(nb_loops * 360):
        alpha = alpha_degrees * degrees_to_radians
        beta = beta_coefficient * alpha
        x, y = get_xy(alpha, beta)
        xs.append(x)
        ys.append(y)
    return xs, ys

def display_print_area():
    xs=[]
    ys=[]
    angle_step = 5
    for alpha_degrees in range(0, 360, angle_step):
        for beta_degrees in range(0, 360, angle_step):
            alpha = alpha_degrees * degrees_to_radians

            beta = beta_degrees * degrees_to_radians
            x, y = get_xy(alpha, beta)
            xs.append(x)
            ys.append(y)
    plt.scatter(xs, ys, c="r")
    plt.axis('equal')
    plt.show()
    return xs, ys


def compute_grid_to_angle(points_per_lego_unit = 4, angle_step = 1):
    grid_to_angle = {}
    gradients = []
    for alpha_degrees in range(0, 360, angle_step):
        alpha = alpha_degrees * degrees_to_radians
        for beta_degrees in range(0, 360, angle_step):
            if 135 < alpha_degrees and alpha_degrees < -135 + 360:
                continue
            if 135 < beta_degrees and beta_degrees < -135 + 360:
                continue
            #print "*" * 100
            #print "alpha", alpha_degrees, "beta", beta_degrees
            beta = beta_degrees * degrees_to_radians
            x, y = get_xy(alpha, beta)
            #print "x:", x, "y:", y
            #x, y = change_referential(x, y)
            x_grid, y_grid = get_closest_grid_point(x, y, points_per_lego_unit)
            #print "x_grid:", x_grid, "y_grid:", y_grid
            distance = compute_distance(x_grid, y_grid, x, y)
            if (x_grid, y_grid) not in grid_to_angle:
                grid_to_angle[(x_grid, y_grid)] = (alpha_degrees, beta_degrees, distance)
            else:
                _, _, best_distance = grid_to_angle[(x_grid, y_grid)]
                if distance < best_distance:
                    grid_to_angle[(x_grid, y_grid)] = (alpha_degrees, beta_degrees, distance)
    distance_threshold = 0.2/points_per_lego_unit
    #result = {a: (x, y, distance) for a, (x, y, distance) in grid_to_angle.items() if distance <= distance_threshold }
    result = grid_to_angle
    #for (x, y), (alpha, beta, d) in grid_to_angle.items():
    #    print x, y, compute_distance(x, y, get_xy(alpha * degrees_to_radians, beta * degrees_to_radians)[0], get_xy(alpha * degrees_to_radians, beta * degrees_to_radians)[1])
    return result

def find_largest_print_area(grid_coordinates, points_per_lego_unit):
    xs = set([x for x, y in grid_coordinates.keys()])
    ys = set([y for x, y in grid_coordinates.keys()])

    xs = sorted(xs, reverse = True)
    ys = sorted(ys)

    min_x = min(xs)
    max_x = max(xs)

    min_y = min(ys)
    max_y = max(ys)

    step = 1/float(points_per_lego_unit)
    result = {}
    for y in ys:
        for x in xs:
            if (x, y) not in grid_coordinates:
                result[(x, y)] = 0
            else:
                if x == min_x or x == max_x or y == min_y or y == max_y:
                    result[(x, y)] = 1
                else:
                    value = min(result[(x + step, y)], result[(x, y - step)], result[(x + step, y - step)]) + 1
                    result[(x, y)] = value
    max_dim = max(result.values())

    top_left_coordinates = []
    for (x, y), dim in result.items():
        if dim == max_dim:
            top_left_coordinates.append((x, y))


def is_rectangle(x0, y0, x1, y1, grid_coordinates, xs, ys):
    for x in xs:
        if x < x0 or x1 < x:
            continue
        for y in ys:
            if y < y0 or y1 < y:
                continue
            if (x, y) not in grid_coordinates:
                return False
    return True

origin = (2.5, 0)
def find_largest_rectange(grid_coordinates):
    xs = set([x for x, y in grid_coordinates.keys()])
    ys = set([y for x, y in grid_coordinates.keys()])

    xs = sorted(list(xs))
    ys = sorted(list(ys))

    min_x = min(xs)
    max_x = max(xs)

    min_y = min(ys)
    max_y = max(ys)
    rectangles = []
    max_area = None
    result = None
    for x_origin in xs:
        for y_origin in ys:
            for x in xs:
                if x < x_origin:
                    continue
                for y in ys:
                    if y < y_origin:
                        continue
                    if is_rectangle(x_origin, y_origin, x, y, grid_coordinates, xs, ys):
                        area = (x-x_origin) * (y-y_origin)
                        if max_area is None or max_area < area:
                            max_area = area
                            result = (x_origin, y_origin, x, y)
    return result

def build_pixel_to_angle(print_area, grid_to_angle):

    xs = set([x for x, y in grid_to_angle.keys()])
    ys = set([y for x, y in grid_to_angle.keys()])
    xs = sorted(list(xs))
    ys = sorted(list(ys))
    x0, y0, x1, y1 = print_area
    xs = [x for x in xs if x0 <= x and x <= x1]
    ys = [y for y in ys if y0 <= y and y <= y1]
    pixel_to_angle = {}
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            pixel_to_angle[i, len(ys) - 1 - j] = grid_to_angle[x, y] #(0, 0) is top left
    return pixel_to_angle

def export_pixel_to_angle(pixel_to_angle):
    xs = set([x for x, y in pixel_to_angle.keys()])
    ys = set([y for x, y in pixel_to_angle.keys()])
    xs = sorted(list(xs))
    ys = sorted(list(ys))
    width = len(xs)
    height = len(ys)
    result_a = []
    result_b = []
    for y in ys:
        for x in xs:
            result_a.append(pixel_to_angle[(x, y)][0])
            result_b.append(pixel_to_angle[(x, y)][1])

    print width, height
    print " ArrayInit(pos_to_alpha, 0, %d);" % (width * height)
    for i, a in enumerate(result_a):
        print " pos_to_alpha[%d] = %d;" % (i, a)
    print " ArrayInit(pos_to_beta, 0, %d);" % (width * height)
    for j, b in enumerate(result_b):
        print " pos_to_beta[%d] = %d;" % (j, b)
    return result_a, result_b

#alpha_degrees = 0
#beta_degrees = 180
#get_xy(alpha_degrees * degrees_to_radians, beta_degrees * degrees_to_radians)
#display_print_area()

x_grids = []
y_grids = []
points_per_lego_unit = 2
grid_to_angle = compute_grid_to_angle(points_per_lego_unit)

#print get_xy(0, 0)
#print get_alpha_beta(0, 9.24, StructureSetting())
#print get_alpha_beta(4, 0, StructureSetting())
#print compute_circle_intersection(-5, 0, 5, 0, 6, 6)

grid_to_angle_backward_kinematics = {}
for (x_grid, y_grid), (alpha, beta, distance) in sorted(grid_to_angle.items()):
    angles = get_alpha_beta(x_grid, y_grid, StructureSetting())
    if angles is None:
        continue
    alpha2, beta2 = angles
    grid_to_angle_backward_kinematics[(x_grid, y_grid)] = (alpha2, beta2, 0)
    #print "***********************"
    #print x_grid, y_grid
    #print alpha, alpha2
    #print beta, beta2
#print "*" * 50
#print get_alpha_beta(-2.5, -5.5, StructureSetting())
#print get_alpha_beta(-2.5, -6, StructureSetting())

grid_to_angle = grid_to_angle_backward_kinematics
print_area = find_largest_rectange(grid_to_angle)

#print_area = (-3.5, 5.0, 2.0, 8.5)
x0, y0, x1, y1 = print_area

pixel_to_angle = build_pixel_to_angle(print_area, grid_to_angle)


for x_grid, y_grid in grid_to_angle.keys():
    x_grids.append(x_grid)
    y_grids.append(y_grid)

#xs_print_area = []
#ys_print_area = []


for b_noise in range(0, 1):
    a_noise = 0
    b_noise = -0
    for a_noise in range(0, 1):
        xs_print_area = []
        ys_print_area = []
        for (x_grid, y_grid), (alpha, beta, d) in pixel_to_angle.items():
            alpha = alpha + a_noise
            beta = beta + b_noise
            x, y = get_xy(alpha * degrees_to_radians, beta * degrees_to_radians)

            x_grids.append(x)
            y_grids.append(y)
            #if x0 <= x_grid and x_grid <= x1 and y0 <= y_grid and y_grid <= y1:
            #if x_grid < 1:
            xs_print_area.append(x)
            ys_print_area.append(y)
        plt.scatter(xs_print_area, ys_print_area, c="b")
        #plt.scatter(pixel_to_angle[(0, 0)][0], pixel_to_angle[(0, 0)][1], c="b")
        plt.axis('equal')
        plt.show()
        export_pixel_to_angle(pixel_to_angle)

"""
print get_xy(102, 33)
print get_xy(91, 28)
print get_xy(81, 76)
print get_xy(71, 20)
print get_xy(273, 56)
print get_xy(279, 25)
"""

#plt.scatter(x_grids, y_grids, c="r")
#plt.scatter(xs_print_area, ys_print_area, c="b")
#plt.scatter(pixel_to_angle[(0, 0)][0], pixel_to_angle[(0, 0)][1], c="b")
#plt.axis('equal')
#plt.show()
