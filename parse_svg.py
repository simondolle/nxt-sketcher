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
    number="[-+]?\d*\.\d+|\d+"
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
        d = {
            "M": MoveTo,
            "L": LineTo,
            "l": LineToRelative,
            "H": HorizontalLineTo,
            "h": HorizontalLineToRelative,
            "V": VerticalLineTo,
            "z": ClosePath,
            "v": VerticalLineToRelative,
            "C": CurveTo,
            "c": CurveToRelative,
            "S": SmoothCurveTo,
            "s": SmoothCurveToRelative,
        }
        result.append(d[command](*params))
    #tokens=re.split("[a-zA-Z]", path)
    return result
    #print tokens


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
        return "M%s"%",".join([str(self.x), str(self.y)])

    def to_nxc(self):
        return "pen_up();\ngoto_point(%s);\npen_down();"%", ".join([str(self.x), str(self.y)])

    def transform(self, transformer):
        x, y = transformer.transform(self.x, self.y)
        return MoveTo(x, y)

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
        return "L%s"%", ".join([str(self.x), str(self.y)])

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
        return "l%s"%", ".join([str(self.x), str(self.y)])

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
        return "H%s"%self.x

    def to_nxc(self):
        return "horizontalLineTo(%s);"%self.x


class HorizontalLineToRelative(MoveTo):
    def __init__(self, x):
        self.x = x

    def draw(self):
        self.draw_line(CURRENT_X + self.x, CURRENT_Y)

    def transform(self, transformer):
        x, _ = transformer.transform_no_shift(self.x, 0)
        return HorizontalLineToRelative(x)

    def __str__(self):
        return "h%s"%self.x

    def to_nxc(self):
        return "horizontalLineToRelative(%s);"%self.x


class VerticalLineTo(MoveTo):
    def __init__(self, y):
        self.y = y

    def draw(self):
        self.draw_line(CURRENT_X, self.y)

    def transform(self, transformer):
        _, y = transformer.transform(0, self.y)
        return VerticalLineTo(y)

    def __str__(self):
        return "V%s"%self.y

    def to_nxc(self):
        return "verticalLineTo(%s);"%self.y


class VerticalLineToRelative(MoveTo):
    def __init__(self, y):
        self.y = y

    def draw(self):
        self.draw_line(CURRENT_X, CURRENT_Y + self.y)

    def transform(self, transformer):
        _, y = transformer.transform_no_shift(0, self.y)
        return VerticalLineToRelative(y)

    def __str__(self):
        return "v%s"%self.y

    def to_nxc(self):
        return "verticalLineToRelative(%s);"%self.y

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
        return "closePath();"


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
        return "C%s"%",".join([str(self.x1), str(self.y1), str(self.x2), str(self.y2), str(self.x), str(self.y)])

    def to_nxc(self):
        return "curve_to(%s);"%", ".join([str(self.x1), str(self.y1), str(self.x2), str(self.y2), str(self.x), str(self.y)])

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
        return "c%s"%",".join([str(self.x1), str(self.y1), str(self.x2), str(self.y2), str(self.x), str(self.y)])

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
        return "S%s"%",".join([str(self.x2), str(self.y2), str(self.x), str(self.y)])

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
        return "s%s"%",".join([str(self.x2), str(self.y2), str(self.x), str(self.y)])

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


path_mona_lisa =("M51.263,23.333c2.549,0.615,6.502,2.458,7.93,6.265c0.83,2.209,0.774,7.062,0.586,10.747   c-0.674,3.906-2.234,6.754-4.662,8.482c-3.25,2.313-7.322,2.075-9.288,1.774c-2.683-1.312-4.266-5.301-4.953-8.557   c-0.804-3.805-0.316-5.789-0.316-5.789V34.83c-0.714-1.903-0.079-7.533,0.872-9.437c0.951-1.903,3.974-1.934,4.837-2.617   c1.208-0.954,2.833-5.08,3.309-6.334c-9.906,1.245-12.379,9.59-12.862,11.806c-1.181,1.126-2.151,3.148-1.163,5.336   c-0.354,0.455-0.71,1.078-0.852,1.861c-0.118,0.654-0.114,1.613,0.443,2.729c-0.984,1.906-3.084,7.236-0.784,14.809   c2.218,7.308,1.275,9.263,0.666,10.154c-1.493,0.588-6.417,2.816-8.482,7.354c-0.591,0.262-1.244,0.684-1.859,1.282V83.65h50.771   V63.17c-1.479-2.172-3.204-4.521-4.703-6.068c-0.412-2.369-2.453-14.255-2.522-18.408c-0.039-2.341-0.129-7.824-2.129-12.791   c-2.328-5.787-6.595-9.064-12.392-9.555h-3.14C46.873,22.421,50.437,23.134,51.263,23.333z M60.541,61.039   c0,0.639,0.248,1.215,0.649,1.646c-0.348,0.307-0.571,0.748-0.571,1.248c0,0.227,0.047,0.44,0.129,0.641   c-0.519,0.484-0.842,1.172-0.842,1.938c0,0.465,0.12,0.9,0.329,1.281c-0.538,0.438-0.887,1.104-0.887,1.852   c0,0.383,0.094,0.744,0.256,1.064c-2.313,1.068-4.934,4.326-4.934,4.326c-5.232,0.396-17.208-1.508-17.684-5.473   c-0.477-3.965,10.864-12.449,10.864-12.449c0-0.488-0.272-2.703-0.48-4.324c0.296,0.016,0.606,0.025,0.928,0.025   c2.354,0,5.341-0.476,7.968-2.338c1.258-0.892,2.314-2.023,3.174-3.38c0.175,5.104,1.338,11.286,1.338,11.286l0.767,0.697   C60.937,59.52,60.541,60.232,60.541,61.039z")

path_frame = "M78.64,86.949H21.495V13.273H78.64V86.949L78.64,86.949z"

paths = [path_mona_lisa, path_frame]
"""
path = ("M99.866,23.353C98.533,10.235,87.456,0,73.988,0C63.193,0,53.938,6.575,50,15.937C46.062,6.575,36.807,0,26.013,0"
	   "C12.544,0,1.466,10.235,0.134,23.353C0.045,24.227,0,25.115,0,26.013c0,31.606,38.788,46.523,50,67.603h0"
	   "c11.212-21.079,50-35.996,50-67.603C100,25.115,99.955,24.227,99.866,23.353z")
"""
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
