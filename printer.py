import math
import matplotlib.pyplot as plt

degrees_to_radians = math.pi / 180
radians_to_degrees = 180 / math.pi

def get_xy(alpha, beta):

    r = 3  # short arm length (attached to the rotative axis)
    a = 8  # long arm length
    b = a + 1  # distance from short arm extremity to pen

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
    gamma = math.acos(math.pow(xd-xe, 2)/float(math.pow(xd-xe, 2) + math.pow(yd-ye, 2)))
    gamma = math.copysign(gamma, ye-yd)

    #lambda is the angle formed by an horizontal axis and the left long arm
    lam = theta + gamma
    xt = xd + b * math.cos(lam)
    yt = yd + b * math.sin(lam)

    return xt, yt

def change_referential(x, y):
    angle = 45 * degrees_to_radians
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

def compute_grid_to_angle(points_per_lego_unit = 4, angle_step = 1):
    grid_to_angle = {}
    for alpha_degrees in range(0, 360, angle_step):
        alpha = alpha_degrees * degrees_to_radians
        for beta_degrees in range(0, 360, angle_step):
            beta = beta_degrees * degrees_to_radians
            x, y = get_xy(alpha, beta)
            x, y = change_referential(x, y)
            x_grid, y_grid = get_closest_grid_point(x, y, points_per_lego_unit)
            distance = compute_distance(x_grid, y_grid, x, y)
            if (x_grid, y_grid) not in grid_to_angle:
                grid_to_angle[(x_grid, y_grid)] = (alpha_degrees, beta_degrees, distance)
            else:
                _, _, best_distance = grid_to_angle[(x_grid, y_grid)]
                if distance < best_distance:
                    grid_to_angle[(x_grid, y_grid)] = (alpha_degrees, beta_degrees, distance)
    distance_threshold = 0.2/points_per_lego_unit
    result = {a: (x, y, distance) for a, (x, y, distance) in grid_to_angle.items() if distance <= distance_threshold }
    return result

def find_largest_print_area(grid_coordinates):
    xs = set([x for x, y in grid_coordinates.keys()])
    ys = set([y for x, y in grid_coordinates.keys()])

    xs = sorted(xs, reverse = True)
    ys = sorted(ys)

    min_x = min(xs)
    max_x = max(xs)

    min_y = min(ys)
    max_y = max(ys)

    step = 0.25
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
    print "nb_points", max_dim
    top_left_coordinates = []
    for (x, y), dim in result.items():
        if dim == max_dim:
            top_left_coordinates.append((x, y))
    print top_left_coordinates

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
    print print_area
    xs = [x for x in xs if x0 <= x and x <= x1]
    ys = [y for y in ys if y0 <= y and y <= y1]
    pixel_to_angle = {}
    print xs
    print ys
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            pixel_to_angle[i, len(ys) - 1 - j] = grid_to_angle[x, y] #(0, 0) is top left
    return pixel_to_angle

x_grids = []
y_grids = []
grid_to_angle = compute_grid_to_angle()
print_area = find_largest_rectange(grid_to_angle)
pixel_to_angle = build_pixel_to_angle(print_area, grid_to_angle)

for x_grid, y_grid in grid_to_angle.keys():
    x_grids.append(x_grid)
    y_grids.append(y_grid)

xs_print_area = []
ys_print_area = []
x0, y0, x1, y1 = print_area
for x_grid, y_grid in grid_to_angle.keys():
    x_grids.append(x_grid)
    y_grids.append(y_grid)
    if x0 <= x_grid and x_grid <= x1 and y0 <= y_grid and y_grid <= y1:
        xs_print_area.append(x_grid)
        ys_print_area.append(y_grid)

alphas = [a for a, b, d in pixel_to_angle.values()]
betas = [b for a, b, d in pixel_to_angle.values()]

plt.scatter(x_grids, y_grids, c="r")
plt.scatter(xs_print_area, ys_print_area, c="b")
plt.axis('equal')
plt.show()
