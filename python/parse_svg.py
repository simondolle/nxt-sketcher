import re
import itertools

CURRENT_X = None
CURRENT_Y = None

LAST_CONTROL_POINT_X = None
LAST_CONTROL_POINT_Y = None

PATH_START_X = None
PATH_START_Y = None

XS = []
YS = []

def parse_params(params):
    number=r"[-+]?\d*\.\d+|[-+]?\d+"
    tokens=re.findall(number, params)
    return [float(f) for f in tokens]


def get_tokens(subtokens):
    for i in range(0, len(subtokens)-1, 2):
        yield (subtokens[i], subtokens[i+1])

def parse_path(path):
    result = []
    subtokens = []
    for k, g in itertools.groupby(path, lambda x: x.isalpha()):
        subtokens.append("".join(g))
    for command, params in get_tokens(subtokens):
        params = parse_params(params)
        print command, params
        d = {
            "M": (MoveTo, 2),
            "m": (MoveToRelative, 2),
            "L": (LineTo, 2),
            "l": (LineToRelative, 2),
            "H": (HorizontalLineTo, 1),
            "h": (HorizontalLineToRelative, 1),
            "V": (VerticalLineTo, 1),
            "z": (ClosePath, 0),
            "v": (VerticalLineToRelative, 1),
            "C": (CurveTo, 6),
            "c": (CurveToRelative, 6),
            "S": (SmoothCurveTo, 4),
            "s": (SmoothCurveToRelative, 4)
        }
        constructor, nb_arguments = d[command]
        for i in range(0, len(params), nb_arguments):
          result.append(constructor(*params[i:i+nb_arguments]))
    return result

def convert_floats(l):
    return ",".join(["{:.2f}".format(x) for x in l])

class MoveTo(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        self.draw_line(self.x, self.y)
        global PATH_START_X
        global PATH_START_Y
        PATH_START_X = self.x
        PATH_START_Y = self.y


    def draw_line(self, x, y):
        #XS.append(CURRENT_X)
        XS.append(x)
        #YS.append(CURRENT_Y)
        YS.append(y)
        global  CURRENT_X
        global CURRENT_Y
        global LAST_CONTROL_POINT_X
        global LAST_CONTROL_POINT_Y
        CURRENT_X = x
        CURRENT_Y = y

        LAST_CONTROL_POINT_X = None
        LAST_CONTROL_POINT_Y = None

    def __str__(self):
        return "M%s"%convert_floats([self.x, self.y])

    def to_nxc(self):
        return "pen_up();\ngoto_point(%s);\npen_down();"%", ".join([str(self.x), str(self.y)])

    def transform(self, transformer):
        x, y = transformer.transform(self.x, self.y)
        return MoveTo(x, y)

class MoveToRelative(MoveTo):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        self.draw_line(self.x + CURRENT_X, self.y + CURRENT_Y)
        global PATH_START_X
        global PATH_START_Y
        PATH_START_X = self.x
        PATH_START_Y = self.y

    def transform(self, transformer):
        x, y = transformer.transform_no_shift(self.x, self.y)
        return MoveToRelative(x, y)

    def __str__(self):
        return "m%s"%convert_floats([self.x, self.y])

    def to_nxc(self):
        return "pen_up();\ngoto_point_relative(%s);\npen_down();"%", ".join([str(self.x), str(self.y)])


class LineTo(MoveTo):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        self.draw_line(self.x, self.y)

    def transform(self, transformer):
        x, y = transformer.transform(self.x, self.y)
        return LineTo(x, y)

    def __str__(self):
        return "L%s"%convert_floats([self.x, self.y])

    def to_nxc(self):
        return "print_line(%s);"%", ".join([str(self.x), str(self.y)])


class LineToRelative(MoveTo):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        self.draw_line(self.x + CURRENT_X, self.y + CURRENT_Y)

    def transform(self, transformer):
        x, y = transformer.transform_no_shift(self.x, self.y)
        return LineToRelative(x, y)

    def __str__(self):
        return "l%s"%convert_floats([self.x, self.y])

    def to_nxc(self):
        return "print_line_relative(%s);"%", ".join([str(self.x), str(self.y)])


class HorizontalLineTo(MoveTo):
    def __init__(self, x):
        self.x = x

    def draw(self):
        self.draw_line(self.x, CURRENT_Y)

    def transform(self, transformer):
        x, _ = transformer.transform(self.x, 0)
        return HorizontalLineTo(x)

    def __str__(self):
        return "H%s"%convert_floats([self.x])

    def to_nxc(self):
        return "horizontal_line_to(%s);"%self.x


class HorizontalLineToRelative(MoveTo):
    def __init__(self, x):
        self.x = x

    def draw(self):
        self.draw_line(CURRENT_X + self.x, CURRENT_Y)

    def transform(self, transformer):
        x, _ = transformer.transform_no_shift(self.x, 0)
        return HorizontalLineToRelative(x)

    def __str__(self):
        return "h%s"%convert_floats([self.x])

    def to_nxc(self):
        return "horizontal_line_to_relative(%s);"%self.x


class VerticalLineTo(MoveTo):
    def __init__(self, y):
        self.y = y

    def draw(self):
        self.draw_line(CURRENT_X, self.y)

    def transform(self, transformer):
        _, y = transformer.transform(0, self.y)
        return VerticalLineTo(y)

    def __str__(self):
        return "V%s"%convert_floats([self.y])

    def to_nxc(self):
        return "vertical_line_to(%s);"%self.y


class VerticalLineToRelative(MoveTo):
    def __init__(self, y):
        self.y = y

    def draw(self):
        self.draw_line(CURRENT_X, CURRENT_Y + self.y)

    def transform(self, transformer):
        _, y = transformer.transform_no_shift(0, self.y)
        return VerticalLineToRelative(y)

    def __str__(self):
        return "v%s"%convert_floats([self.y])

    def to_nxc(self):
        return "vertical_line_to_relative(%s);"%self.y

class ClosePath(MoveTo):
    def __init__(self):
        pass
    def draw(self):
        self.draw_line(PATH_START_X, PATH_START_Y)
        global PATH_START_X
        PATH_START_X = None
        global PATH_START_Y
        PATH_START_Y = None

    def transform(self, transformer):
        return ClosePath()

    def __str__(self):
        return "z"

    def to_nxc(self):
        return "close_path();"


class CurveTo(object):
    def __init__(self, x1, y1, x2, y2, x, y):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x = x
        self.y = y

        self.t_step = 0.05

    def draw(self):
        self.draw_curve(self.x1, self.y1, self.x2, self.y2, self.x, self.y)

    def draw_curve(self, x1, y1, x2, y2, x, y):

        global CURRENT_X
        global CURRENT_Y


        t = 0.0
        x0 = CURRENT_X
        y0 = CURRENT_Y

        while(t < 1.0):
            target_x = (1-t)*(1-t)*(1-t) * x0 + 3*(1-t)*(1-t)* t * x1 + 3*(1-t)* t * t * x2 + t*t*t*x
            target_y = (1-t)*(1-t)*(1-t) * y0 + 3*(1-t)*(1-t)* t * y1 + 3*(1-t)* t * t * y2 + t*t*t*y
            XS.append(target_x)
            YS.append(target_y)
            t += self.t_step
        XS.append(x)
        YS.append(y)
        CURRENT_X = x
        CURRENT_Y = y

        global LAST_CONTROL_POINT_X
        global LAST_CONTROL_POINT_Y
        LAST_CONTROL_POINT_X = x2
        LAST_CONTROL_POINT_Y = y2

    def transform(self, transformer):
        x1, y1 = transformer.transform(self.x1, self.y1)
        x2, y2 = transformer.transform(self.x2, self.y2)
        x, y = transformer.transform(self.x, self.y)
        return CurveTo(x1, y1, x2, y2, x, y)

    def __str__(self):
        return "C%s"%convert_floats([self.x1, self.y1, self.x2, self.y2, self.x, self.y])

    def to_nxc(self):
        return "curve_to(%s);"%convert_floats([self.x1, self.y1, self.x2, self.y2, self.x, self.y])

class CurveToRelative(CurveTo):
    def __init__(self, x1, y1, x2, y2, x, y):
        super(CurveToRelative, self).__init__(x1, y1, x2, y2, x, y)

    def draw(self):
        self.current_x = CURRENT_X
        self.current_y = CURRENT_Y
        self.draw_curve(self.x1 + CURRENT_X, self.y1 + CURRENT_Y, self.x2 + CURRENT_X, self.y2 + CURRENT_Y, self.x + CURRENT_X, self.y + CURRENT_Y)

    def transform(self, transformer):
        x1, y1 = transformer.transform_no_shift(self.x1, self.y1)
        x2, y2 = transformer.transform_no_shift(self.x2, self.y2)
        x, y = transformer.transform_no_shift(self.x, self.y)
        return CurveToRelative(x1, y1, x2, y2, x, y)

    def __str__(self):
        return "c%s"%convert_floats([self.x1, self.y1, self.x2, self.y2, self.x, self.y])

    def to_nxc(self):
        return "curve_to_relative(%s);"%", ".join([str(self.x1), str(self.y1), str(self.x2), str(self.y2), str(self.x), str(self.y)])

class SmoothCurveTo(CurveTo):
    def __init__(self, x2, y2, x, y):
        super(SmoothCurveTo, self).__init__(None, None, x2, y2, x, y)

    def get_x1_y1(self):
        if LAST_CONTROL_POINT_X is not None:
            x1 = CURRENT_X + CURRENT_X - LAST_CONTROL_POINT_X
            y1 = CURRENT_Y + CURRENT_Y - LAST_CONTROL_POINT_Y
        else:
            x1 = CURRENT_X
            y1 = CURRENT_Y
        return x1, y1

    def draw(self):
        x1, y1 = self.get_x1_y1()
        self.draw_curve(x1, y1, self.x2, self.y2, self.x, self.y)

    def transform(self, transformer):
        x2, y2 = transformer.transform(self.x2, self.y2)
        x, y = transformer.transform(self.x, self.y)
        return SmoothCurveTo(x2, y2, x, y)

    def __str__(self):
        return "S%s"%convert_floats([self.x2, self.y2, self.x, self.y])

    def to_nxc(self):
        return "smooth_curve_to(%s);"%", ".join([str(self.x2), str(self.y2), str(self.x), str(self.y)])


class SmoothCurveToRelative(SmoothCurveTo):
    def __init__(self, x2, y2, x, y):
        super(SmoothCurveToRelative, self).__init__(x2, y2, x, y)

    def draw(self):
        self.current_x = CURRENT_X
        self.current_y = CURRENT_Y

        x1, y1 = self.get_x1_y1()
        self.draw_curve(x1, y1, self.x2 + CURRENT_X, self.y2 + CURRENT_Y, self.x + CURRENT_X, self.y + CURRENT_Y)

    def transform(self, transformer):
        x2, y2 = transformer.transform_no_shift(self.x2, self.y2)
        x, y = transformer.transform_no_shift(self.x, self.y)
        return SmoothCurveToRelative(x2, y2, x, y)

    def __str__(self):
        return "s%s"%convert_floats([self.x2, self.y2, self.x, self.y])

    def to_nxc(self):
        return "smooth_curve_to_relative(%s);"%", ".join([str(self.x2), str(self.y2), str(self.x), str(self.y)])


class CoordinateTransformer(object):
    def transform(self, x, y):
        return x, y

    def transform_no_shift(self, x, y):
        return x, y


class TranslationTransformer(object):
    def __init__(self, x_shift, y_shift, coordinate_transformer):
        self.x_shift = x_shift
        self.y_shift = y_shift
        self.coordinate_transformer = coordinate_transformer

    def transform(self, x, y):
        x, y = self.coordinate_transformer.transform(x, y)
        return x + self.x_shift, y + self.y_shift

    def transform_no_shift(self, x, y):
        return x, y

class ScaleTransformer(object):
    def __init__(self, scale_ratio, coordinate_transformer):
        self.scale_ratio = scale_ratio
        self.coordinate_transformer = coordinate_transformer

    def transform(self, x, y):
        x, y = self.coordinate_transformer.transform(x, y)
        return self.scale_ratio * x, self.scale_ratio * y

    def transform_no_shift(self, x, y):
        x, y = self.coordinate_transformer.transform_no_shift(x, y)
        return self.scale_ratio * x, self.scale_ratio * y

input_path = "/Users/simon/Downloads/noun_130928.xml"
import sys
input_path = sys.argv[1]
c = open(input_path).read()

path_regex = 'path d="(.*?)"'
paths = re.findall(path_regex, c)
print paths

#path_mona_lisa =("M51.263,23.333c2.549,0.615,6.502,2.458,7.93,6.265c0.83,2.209,0.774,7.062,0.586,10.747   c-0.674,3.906-2.234,6.754-4.662,8.482c-3.25,2.313-7.322,2.075-9.288,1.774c-2.683-1.312-4.266-5.301-4.953-8.557   c-0.804-3.805-0.316-5.789-0.316-5.789V34.83c-0.714-1.903-0.079-7.533,0.872-9.437c0.951-1.903,3.974-1.934,4.837-2.617   c1.208-0.954,2.833-5.08,3.309-6.334c-9.906,1.245-12.379,9.59-12.862,11.806c-1.181,1.126-2.151,3.148-1.163,5.336   c-0.354,0.455-0.71,1.078-0.852,1.861c-0.118,0.654-0.114,1.613,0.443,2.729c-0.984,1.906-3.084,7.236-0.784,14.809   c2.218,7.308,1.275,9.263,0.666,10.154c-1.493,0.588-6.417,2.816-8.482,7.354c-0.591,0.262-1.244,0.684-1.859,1.282V83.65h50.771   V63.17c-1.479-2.172-3.204-4.521-4.703-6.068c-0.412-2.369-2.453-14.255-2.522-18.408c-0.039-2.341-0.129-7.824-2.129-12.791   c-2.328-5.787-6.595-9.064-12.392-9.555h-3.14C46.873,22.421,50.437,23.134,51.263,23.333z M60.541,61.039   c0,0.639,0.248,1.215,0.649,1.646c-0.348,0.307-0.571,0.748-0.571,1.248c0,0.227,0.047,0.44,0.129,0.641   c-0.519,0.484-0.842,1.172-0.842,1.938c0,0.465,0.12,0.9,0.329,1.281c-0.538,0.438-0.887,1.104-0.887,1.852   c0,0.383,0.094,0.744,0.256,1.064c-2.313,1.068-4.934,4.326-4.934,4.326c-5.232,0.396-17.208-1.508-17.684-5.473   c-0.477-3.965,10.864-12.449,10.864-12.449c0-0.488-0.272-2.703-0.48-4.324c0.296,0.016,0.606,0.025,0.928,0.025   c2.354,0,5.341-0.476,7.968-2.338c1.258-0.892,2.314-2.023,3.174-3.38c0.175,5.104,1.338,11.286,1.338,11.286l0.767,0.697   C60.937,59.52,60.541,60.232,60.541,61.039z")

#path_frame = "M78.64,86.949H21.495V13.273H78.64V86.949L78.64,86.949z"

#paths = [path_mona_lisa, path_frame]
"""
path = ("M99.866,23.353C98.533,10.235,87.456,0,73.988,0C63.193,0,53.938,6.575,50,15.937C46.062,6.575,36.807,0,26.013,0"
	   "C12.544,0,1.466,10.235,0.134,23.353C0.045,24.227,0,25.115,0,26.013c0,31.606,38.788,46.523,50,67.603h0"
	   "c11.212-21.079,50-35.996,50-67.603C100,25.115,99.955,24.227,99.866,23.353z")
"""

#paths = ["M72.748,0C55.736,0,50,15.099,50,15.099S44.271,0,27.252,0C10.245,0,0,16.214,0,29.578c0,22.396,50,56.53,50,56.53s50-34.126,50-56.526C100,16.214,89.76,0,72.748,0z"]

#paths = ["M34.305,31.591c0.106-0.18,0.172-0.386,0.146-0.61c-0.346-3.019-5.377-6.307-8.935-2.071    c-0.836,0.997,0.681,2.271,1.517,1.273c1.253-1.49,2.825-1.783,4.418-0.538c-1.092-0.252-3.334-0.275-4.946,1.836    c-0.375,0.494-0.213,1.208,0.343,1.485c3.229,1.617,4.774,1.159,6.832,0.116C33.681,33.083,34.869,32.613,34.305,31.591z     M29.161,31.787c0.787-0.383,1.748-0.369,2.522,0.042C30.956,32.099,30.203,32.116,29.161,31.787z M90.421,83.053    c-10.293-9.495-15.23-28.516-16.903-42.984c-0.645-4.864-1.057-9.359-1.396-13.063C70.714,11.646,59.651,0.5,45.818,0.5    c-10.92,0-20.382,7.248-22.884,16.676c-6.322,5.436-7.131,12.174-5.22,15.549c-3.38,9.669-3.378,21.59,2.353,32.572    c-1.044,6.317-2.582,11.803-4.846,15.602c-2.039,1.148-3.959,2.516-5.698,4.105c-1.072,0.976,0.476,2.249,1.336,1.461    c2.786-2.544,6.049-4.51,9.563-5.8c-2.51,3.154-4.661,6.621-6.291,10.279c-0.564,1.263,1.302,1.939,1.809,0.806    c0.547-1.226,1.157-2.431,1.818-3.609c2.163,7.872,18.556,11.807,32.736,11.318h0.001c0,0,0.001,0,0.002,0    c0.289-0.025,0.512-0.107,0.688-0.279c12.487-12.103,29.561-19.231,38.071-14.513C90.34,85.487,91.479,83.766,90.421,83.053z     M40.961,3.035c14.151-3.22,28.619,7.695,29.45,26.978C62.323,13.261,43.223,10.056,37.465,9.701    C37.741,7.577,38.856,4.639,40.961,3.035z M40.276,11.994c-1.235-0.029-5.454-0.263-8.211,0.483    C33.652,11.963,36.091,11.235,40.276,11.994z M37.386,4.169c-1.151,1.886-1.753,4.01-1.92,5.603    c-3.289,0.309-6.398,1.479-8.52,3.152C29.291,9.1,33.002,5.975,37.386,4.169z M19.733,32.935c0.129-0.349-0.024-0.78-0.154-0.953    c-0.993-1.256-1.478-6.538,3.163-11.806c-0.249,2.202-0.461,28.834-2.15,41.595C16.521,52.306,16.447,41.984,19.733,32.935z     M18.221,79.416c4.058-8.896,5.391-23.229,5.827-37.384c1.916,9.923,6.874,16.813,12.15,18.902    c0.084,2.57,0.604,4.839,1.084,6.422c-5.251,2.279-10.245,5.947-14.46,10.502C21.249,78.253,19.711,78.777,18.221,79.416z     M55.821,92.586c-1.993,1.523-3.91,3.165-5.721,4.898c-8.642,0-13.638-0.721-18.304-1.991c0.252-0.325,0.631-0.678,1.215-0.934    c1.206-0.525,0.409-2.347-0.794-1.813c-1.304,0.569-2.01,1.466-2.393,2.165c-6.259-2.028-10.312-5.042-10.312-8.341    c0-4.106,11.375-14.667,18.423-17.341c0.517,1.131,2.379,0.438,1.8-0.826c-0.4-0.867-1.307-3.404-1.529-6.91    c2.689,0.426,12.537-0.393,21.073-8.927c0.923-0.923-0.478-2.323-1.399-1.398c-4.21,4.209-11.52,8.457-18.354,8.457    c-13.385,0-17.417-30.015-13.39-42.355c5.905-4.972,23.144-3.693,25.796-0.83c0.005,0.005,0.013,0.007,0.019,0.012    c12.849,14.817,6.392,73.741,3.877,76.124C55.827,92.578,55.825,92.584,55.821,92.586z M58.702,90.512    c4.039-14.891,5.387-59.84-4.165-73.902c7.404,3.927,14.837,10.951,16.994,23.525c1.806,13.708,5.449,30.441,14.556,41.236    C80.063,80.11,69.402,83.161,58.702,90.512z M51.38,29.236c-0.265-0.067-0.735-0.427-1.019-0.613    c-6.84-4.477-10.925,1.111-11.215,1.513c-0.838,1.159,0.893,2.144,1.604,1.158c1.059-1.467,3.854-4.071,8.738-0.879    c0.678,0.443,1.213,0.792,1.811,0.792C52.6,31.207,52.729,29.438,51.38,29.236z M40.979,31.461    c-0.403,0.5-0.233,1.244,0.345,1.518c3.955,2.171,6.67,0.315,7.393,0c0.521-0.248,0.782-0.973,0.346-1.517    C46.971,28.865,43.062,28.889,40.979,31.461z M43.708,31.786c0.848-0.381,1.886-0.366,2.718,0.042    C45.643,32.097,44.822,32.118,43.708,31.786z M42.492,47.848c-2.445,0.746-3.695-0.551-6.395,0.496    c-0.894,0-1.597-0.906-3.76-0.454c-1.268,0.062-1.176,2.011,0.097,1.978c0.362,0,0.706-0.122,1.07-0.122    c0.573,0,1.656,0.586,2.741,0.586c0.488,0,1.16-0.463,1.854-0.463c0.338,0,1.455,0.152,1.361,0.18    c-1.775,0.536-4.078,0.471-4.95,0.055c-1.163-0.554-2.017,1.233-0.852,1.787c1.415,0.675,4.296,0.683,6.373,0.054    c0.927-0.278,0.983-1.711-0.113-1.911c1.095,0.072,2.379,0.056,3.361-0.367C44.478,49.148,43.691,47.332,42.492,47.848z     M32.607,39.949l-0.784,3.007c-0.114,0.56,0.133,1.378,0.963,1.43c2.361,3.619,6.151,0.107,6.473,0.167    c0.991,0.837,2.322-0.625,1.334-1.466c-1.235-1.047-2.392-0.289-3.161,0.214c-2.718,1.657-2.563,0.095-3.43-0.479l0.539-2.446    C34.829,39.069,32.896,38.644,32.607,39.949z"]

operation_sets = [parse_path(p) for p in paths]

#import sys
#sys.exit(0)

CURRENT_X = 0
CURRENT_Y = 0
"""
operations = []
operations.append(MoveTo(72.748, 0))
operations.append(CurveTo(55.736, 0, 50, 15.099, 50, 15.099))
operations.append(SmoothCurveTo(44.271, 0, 27.252, 0))
operations.append(CurveTo(10.245, 0, 0, 16.214, 0, 29.578))
operations.append(CurveToRelative(0, 22.396, 50, 56.53, 50, 56.53))
operations.append(SmoothCurveToRelative(50, -34.126, 50, -56.526))
operations.append(CurveTo(100, 16.214, 89.76, 0, 72.748, 0))
"""

for operations in operation_sets:
    for operation in operations:
        operation.draw()

# min(XS), max(XS)
#print min(YS), max(YS)

"""
width = 4.25
height = 4.25
"""
width = 6.5
height = 4


points_per_lego_unit = 3




transformer = CoordinateTransformer()
transformer = TranslationTransformer(-min(XS), -min(YS), transformer)
scale_x = width * points_per_lego_unit /(max(XS) - min(XS))
scale_y = height * points_per_lego_unit /(max(YS) - min(YS))
transformer = ScaleTransformer(min(scale_x, scale_y), transformer)

operations_sets_scaled = []
for operations in operation_sets:
    operations_scaled = [op.transform(transformer) for op in operations]
    operations_sets_scaled.append(operations_scaled)


XS = []
YS = []
CURRENT_X = 0
CURRENT_Y = 0

LAST_CONTROL_POINT_X = None
LAST_CONTROL_POINT_Y = None

for operations in operations_sets_scaled:
    for operation in operations:
        print operation.to_nxc();
print "pen_up();"

for operations in operation_sets:
    for operation in operations:
        operation.draw()
#print min(XS), max(XS)
#print min(YS), max(YS)

import matplotlib.pyplot as plt

plt.plot(XS, YS, 'b-')

plt.gca().invert_yaxis()
plt.axis('equal')
plt.show()
