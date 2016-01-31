CURRENT_X = None
CURRENT_Y = None

LAST_CONTROL_POINT_X = None
LAST_CONTROL_POINT_Y = None

XS = []
YS = []

class MoveTo(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        #XS.append(CURRENT_X)
        XS.append(self.x)
        #YS.append(CURRENT_Y)
        YS.append(self.y)
        global  CURRENT_X
        global CURRENT_Y
        global LAST_CONTROL_POINT_X
        global LAST_CONTROL_POINT_Y
        CURRENT_X = self.x
        CURRENT_Y = self.y

        LAST_CONTROL_POINT_X = None
        LAST_CONTROL_POINT_Y = None

    def __str__(self):
        return "M%s"%",".join([str(self.x), str(self.y)])

    def to_nxc(self):
        return "goto_position(%s);\npen_down();"%", ".join([str(self.x), str(self.y)])

    def transform(self, transformer):
        x, y = transformer.transform(self.x, self.y)
        return MoveTo(x, y)

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

"""
M 72.748, 0
C 55.736, 0, 50, 15.099, 50, 15.099
S 44.271, 0, 27.252, 0
C 10.245, 0, 0, 16.214, 0, 29.578
c 0, 22.396, 50, 56.53, 50, 56.53
s 50 -34.126, 50 -56.526
C 100 16.214 89.76 0 72.748 0
"""

CURRENT_X = 0
CURRENT_Y = 0
operations = []
operations.append(MoveTo(72.748, 0))
operations.append(CurveTo(55.736, 0, 50, 15.099, 50, 15.099))
operations.append(SmoothCurveTo(44.271, 0, 27.252, 0))
operations.append(CurveTo(10.245, 0, 0, 16.214, 0, 29.578))
operations.append(CurveToRelative(0, 22.396, 50, 56.53, 50, 56.53))
operations.append(SmoothCurveToRelative(50, -34.126, 50, -56.526))
operations.append(CurveTo(100, 16.214, 89.76, 0, 72.748, 0))

for operation in operations:
    operation.draw()

#print min(XS), max(XS)
#print min(YS), max(YS)

width = 4.25 - 0.5;
height = 4.25 - 0.5;
points_per_lego_unit = 3;


transformer = CoordinateTransformer()
transformer = TranslationTransformer(-min(XS), -min(YS), transformer)
scale_x = width * points_per_lego_unit /(max(XS) - min(XS))
scale_y = height * points_per_lego_unit /(max(YS) - min(YS))
transformer = ScaleTransformer(min(scale_x, scale_y), transformer)

operations_scaled = [op.transform(transformer) for op in operations]
XS = []
YS = []
CURRENT_X = 0
CURRENT_Y = 0

LAST_CONTROL_POINT_X = None
LAST_CONTROL_POINT_Y = None

for operation in operations_scaled:
    print operation.to_nxc();
print "pen_up();"

for operation in operations_scaled:
    operation.draw()
#print min(XS), max(XS)
#print min(YS), max(YS)


import matplotlib.pyplot as plt

plt.plot(XS, YS, 'b-')

plt.gca().invert_yaxis()
plt.axis('equal')
plt.show()
