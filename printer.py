import math
import matplotlib.pyplot as plt

def get_xy(alpha, beta):

    r = 3
    a = 8
    b = a + 1

    xa = -5
    xb = 5

    xd = xa - r * math.sin(alpha)
    yd = r * math.cos(alpha)

    xe = xb - r * math.sin(beta)
    ye = r * math.cos(beta)

    de = compute_distance(xd, yd, xe, ye)

    cos_theta = de/float(2 * a)
    cos_theta = min(cos_theta, 1.0)
    cos_theta = max(cos_theta, -1.0)
    theta = math.acos(cos_theta)

    gamma = math.acos(math.pow(xd-xe, 2)/float(math.pow(xd-xe, 2) + math.pow(yd-ye, 2)))
    gamma = math.copysign(gamma, ye-yd)

    lam = theta + gamma
    xt = xd + b * math.cos(lam)
    yt = yd + b * math.sin(lam)

    return xt, yt

def get_closest_grid_point(x, y, points_per_lego_unit = 2):
    x_grid = round(x * points_per_lego_unit) / float(points_per_lego_unit)
    y_grid = round(y * points_per_lego_unit) / float(points_per_lego_unit)
    return x_grid, y_grid

def compute_distance(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2-x1, 2) + math.pow(y2-y1, 2))

degrees_to_radians = math.pi / 180
radians_to_degrees = 180 / math.pi


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

def compute_grid_to_angle(points_per_lego_unit = 3, angle_step = 1):
    grid_to_angle = {}
    for alpha_degrees in range(0, 360, angle_step):
        alpha = alpha_degrees * degrees_to_radians
        for beta_degrees in range(0, 360, angle_step):
            beta = beta_degrees * degrees_to_radians
            x, y = get_xy(alpha, beta)
            x_grid, y_grid = get_closest_grid_point(x, y, points_per_lego_unit)
            distance = compute_distance(x_grid, y_grid, x, y)
            if (x_grid, y_grid) not in grid_to_angle:
                grid_to_angle[(x_grid, y_grid)] = (x, y, distance)
            else:
                best_x, best_y, best_distance = grid_to_angle[(x_grid, y_grid)]
                if distance < best_distance:
                    grid_to_angle[(x_grid, y_grid)] = (x, y, distance)
    distance_threshold = 0.2/points_per_lego_unit
    result = {a: (x, y, distance) for a, (x, y, distance) in grid_to_angle.items() if distance <= distance_threshold }
    return result

x_grids = []
y_grids = []
grid_to_angle = compute_grid_to_angle()
for x_grid, y_grid, distance in grid_to_angle.values():
    x_grids.append(x_grid)
    y_grids.append(y_grid)

plt.scatter(x_grids, y_grids, c="r")
plt.axis('equal')
plt.show()
