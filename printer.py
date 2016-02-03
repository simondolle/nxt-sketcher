import argparse
import math
import numpy as np
import matplotlib.pyplot as plt


degrees_to_radians = math.pi / 180
radians_to_degrees = 180 / math.pi

def get_xy(alpha, beta, structure_settings):

    r = structure_settings.r  # short arm length (attached to the rotative axis)
    a = structure_settings.a  # long arm length
    s = structure_settings.s  # pen distance

    xa = structure_settings.xa #left short arm x
    xb = structure_settings.xb #right short arm x


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
    tan_gamma = (ye-yd)/float(xe-xd)
    gamma = math.atan(tan_gamma)

    #lambda is the angle formed by an horizontal axis and the left long arm
    lam = theta + gamma
    xt = xd + a * math.cos(lam) - s * math.sin(lam)
    yt = yd + a * math.sin(lam) + s * math.cos(lam)

    return xt, yt

class StructureSetting:
    def __init__(self):
        self.r = 3  # short arm length (attached to the rotative axis)
        self.a = 12  # long arm length
        self.s = 1  # pen distance

        self.xa = -5 #left short arm x
        self.xb = 5 #right short arm x

        self.gear_ratio = 3

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
    return (x3, y3), (x3_prime, y3_prime)


def get_alpha_beta(x, y, structure_settings):
    r_pen = math.sqrt(math.pow(structure_settings.a, 2) + math.pow(structure_settings.s, 2))

    intersection1 = compute_circle_intersection(structure_settings.xa, 0, x, y, structure_settings.r, r_pen)
    if intersection1 is None:
        return None
    (x1, y1), (x1_prime, y1_prime) = intersection1
    alpha = math.atan2(structure_settings.xa - x1, y1) * radians_to_degrees
    alpha_prime = math.atan2(structure_settings.xa - x1_prime, y1_prime) * radians_to_degrees

    if x1 < x1_prime:
        alpha_result = alpha
        x1_actual = x1
        y1_actual = y1
    else:
        alpha_result = alpha_prime
        x1_actual = x1_prime
        y1_actual = y1_prime

    intersection_cross = compute_circle_intersection(x1_actual, y1_actual, x, y, structure_settings.a, structure_settings.s)
    if intersection_cross is None:
        return None
    (x_cross, y_cross), (x_cross_prime, y_cross_prime) = intersection_cross
    if (x_cross - x1_actual) * (y - y_cross) - (y_cross - y1_actual) * (x - x_cross) > 0:
        x_cross_actual = x_cross
        y_cross_actual = y_cross
    else:
        x_cross_actual = x_cross_prime
        y_cross_actual = y_cross_prime

    intersection2 = compute_circle_intersection(structure_settings.xb, 0, x_cross_actual, y_cross_actual, structure_settings.r, structure_settings.a)
    if intersection2 is None:
        return None
    (x2, y2), (x2_prime, y2_prime) = intersection2

    beta = math.atan2(structure_settings.xb - x2, y2) * radians_to_degrees
    beta_prime = math.atan2(structure_settings.xb - x2_prime, y2_prime) * radians_to_degrees

    if x2 > x2_prime:
        beta_result = beta
    else:
        beta_result = beta_prime

    result =  alpha_result, beta_result

    if alpha_result < -135 or 135 < alpha_result:
        return None

    if beta_result < -135 or 135 < beta_result:
        return None

    return result


def change_referential(x, y, angle):
    angle = angle * degrees_to_radians
    return (x * math.cos(angle)  + y * math.sin(angle), -x * math.sin(angle) + y * math.cos(angle))

def compute_distance(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2-x1, 2) + math.pow(y2-y1, 2))

def compute_grid_to_angle_inverse_kinematics(structure_settings, points_per_lego_unit = 4, angle = -30):
    grid_to_angle = {}
    for x in np.arange(-10, 10 + 1, 1/float(points_per_lego_unit)):
      for y in np.arange(0, 15, 1/float(points_per_lego_unit) ):
        x_prime, y_prime = change_referential(x, y, angle)

        angles = get_alpha_beta(x_prime, y_prime, structure_settings)
        if angles is None:
          continue
        grid_to_angle[(x, y)] = (round(structure_settings.gear_ratio * angles[0]), round(structure_settings.gear_ratio * angles[1]), 0)
    return grid_to_angle


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return str((self.x, self.y))

def area(ll, ur):
    return math.fabs((ll.x - ur.x) * (ll.y - ur.y))

def grow_ones(ll, N, M, points, step, cache):
    ur = Point(ll.x-step, ll.y-step) # Zero area ur-choice
    x_max = N # Right edge of growth zone
    y = ll.y-step
    while y + step <= M and (ll.x, y + step) in points:
       y = y + step
       x = min(ll.x + cache[y] - step, x_max)
       x_max = x
       if area(ll, Point(x, y)) > area(ll, ur):
          ur = Point(x, y)
    return ur

def update_cache(x, cache, points, ys, step):
    for y in ys:
        if (x, y) in points:
            cache[y] = cache[y] + step
        else:
            cache[y] = 0
    return cache

def find_largest_rectange_quadratic(grid_coordinates, points_per_lego_unit):
    xs = set([x for x, y in grid_coordinates.keys()])
    ys = set([y for x, y in grid_coordinates.keys()])

    xs = sorted(list(xs))
    ys = sorted(list(ys))

    min_x = min(xs)
    max_x = max(xs)

    min_y = min(ys)
    max_y = max(ys)

    points = set(grid_coordinates.keys())
    step  = 1./points_per_lego_unit

    cache = {}
    for y in ys:
        cache[y] = 0

    best_ll = Point(xs[0], ys[0])
    best_ur = Point(xs[0], ys[0])
    for x in sorted(xs, reverse=True):
        cache = update_cache(x, cache, points, ys, step)
        for y in ys:
            ll = Point(x, y)
            ur = grow_ones(ll, max_x, max_y, points, step, cache)
            if area(ll, ur) > area(best_ll, best_ur):
                best_ll = ll
                best_ur = ur
    return (best_ll.x, best_ll.y, best_ur.x, best_ur.y)

def compute_error(x, y):
    structure_settings = StructureSetting()
    #x, y = change_referential(x, y, 0)
    r = get_alpha_beta(x, y, structure_settings)
    if r is None:
        return -0.1
    alpha, beta = r

    alpha = alpha * degrees_to_radians
    beta = beta * degrees_to_radians
    distances = []
    angle_error = 1.0
    for alpha_shift in [-angle_error * degrees_to_radians, 0, angle_error * degrees_to_radians]:
        for beta_shift in [-angle_error * degrees_to_radians, 0, angle_error * degrees_to_radians]:
            x_shift, y_shift = get_xy(alpha + alpha_shift, beta + beta_shift, structure_settings)
            distance = compute_distance(x, y, x_shift, y_shift)

            distances.append(distance)
    return max(distances)

def display_reachable_area(points_per_lego_unit, angle, plot_errors):
    reachable_xs = []
    reachable_ys = []
    grid_to_angle = compute_grid_to_angle_inverse_kinematics(StructureSetting(), points_per_lego_unit, angle)
    for (x, y), (alpha, beta, _) in grid_to_angle.items():
        x, y = change_referential(x, y, angle)
        reachable_xs.append(x)
        reachable_ys.append(y)

    print_area = find_largest_rectange_quadratic(grid_to_angle, points_per_lego_unit)
    x0, y0, x1, y1 = print_area

    xt0, yt0 = change_referential(x0, y0, angle)
    xt1, yt1 = change_referential(x0, y1, angle)
    xt2, yt2 = change_referential(x1, y1, angle)
    xt3, yt3 = change_referential(x1, y0, angle)

    margin = 1

    min_xs = min(reachable_xs) - margin
    max_xs = max(reachable_xs) + margin

    min_ys = min(reachable_ys) - margin
    max_ys = max(reachable_ys) + margin

    if plot_errors:
        xi = np.linspace(min_xs, max_xs, 100)
        yi = np.linspace(min_ys, max_ys, 100)
        X, Y = np.meshgrid(xi, yi)
        errors = np.vectorize(compute_error)(X, Y)

        CS = plt.contourf(X, Y, errors, 15, cmap=plt.cm.rainbow, vmax=abs(errors).max(), vmin=0)
        plt.colorbar(CS)

    plt.scatter(reachable_xs, reachable_ys, marker='o', c='b', s=5)
    plt.plot([xt0, xt1, xt2, xt3, xt0], [yt0, yt1, yt2, yt3, yt0])

    plt.axis('equal')
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--reachable', action='store_true')
    parser.add_argument('--error', action='store_true')
    parser.add_argument('-p', metavar='N', type=int, default=4, help='points per lego unit')
    parser.add_argument('-a', metavar='N', type=int, default=-45, help='angle')

    points_per_lego_unit = 4
    args = parser.parse_args()

    if args.reachable is True:
        display_reachable_area(args.p, args.a, args.error)
