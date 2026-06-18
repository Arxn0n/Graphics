import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

def is_left_of_line(point, line_start, line_end):
    """
    Определяет, находится ли точка слева от линии, заданной отрезком (line_start, line_end).
    Возвращает:
        > 0, если точка слева,
        = 0, если точка на линии,
        < 0, если точка справа.
    """
    return (line_end[0] - line_start[0]) * (point[1] - line_start[1]) - \
           (line_end[1] - line_start[1]) * (point[0] - line_start[0])

def is_shadow_cast(line1, line2, light):
    """
    Определяет, будет ли тень от одного отрезка падать на другой.
    Возвращает:
        True, если тень от одного отрезка падает на другой,
        False, если тень не падает.
    """
    A1, A2 = line1  # Первая линия
    B1, B2 = line2  # Вторая линия

    # Определяем положение источника света относительно каждого отрезка
    left_of_line1 = is_left_of_line(light, A1, A2)
    left_of_line2 = is_left_of_line(light, B1, B2)

    # Если отрезки находятся на одной стороне от источника света, тень не падает
    if (left_of_line1 > 0 and left_of_line2 > 0) or (left_of_line1 < 0 and left_of_line2 < 0):
        return False

    # Если отрезки параллельны и находятся на одинаковом расстоянии от источника света, тень не падает
    if np.isclose(left_of_line1, left_of_line2, atol=1e-10):
        return False

    # Если расстояние между отрезками слишком велико, тень не падает
    dist_line1 = np.linalg.norm(np.array(A1) - np.array(B1))
    dist_line2 = np.linalg.norm(np.array(A2) - np.array(B2))
    if dist_line1 > 1e6 or dist_line2 > 1e6:
        return False

    # Во всех остальных случаях тень падает
    return True

def determine_shadow_caster(light, line1, line2):
    """
    Определяет, от какого отрезка падает тень.
    Возвращает тот отрезок, который находится ближе к источнику света и отбрасывает тень на другой отрезок.
    """
    A1, A2 = line1  # Первая линия
    B1, B2 = line2  # Вторая линия

    # Вычисляем среднюю точку каждого отрезка
    mid_line1 = [(A1[0] + A2[0]) / 2, (A1[1] + A2[1]) / 2]
    mid_line2 = [(B1[0] + B2[0]) / 2, (B1[1] + B2[1]) / 2]

    # Вычисляем расстояние от источника света до средней точки каждого отрезка
    dist_line1 = np.linalg.norm(np.array(light) - np.array(mid_line1))
    dist_line2 = np.linalg.norm(np.array(light) - np.array(mid_line2))

    # Определяем, какой отрезок ближе к источнику света
    if dist_line1 < dist_line2:
        return line1, line2  # Первый отрезок отбрасывает тень на второй
    else:
        return line2, line1  # Второй отрезок отбрасывает тень на первый
    
def angle(point, source):
    """Вычисляет угол между точкой и источником относительно оси X"""
    vector = np.array(point) - np.array(source)
    return np.arctan2(vector[1], vector[0])  # atan2 дает угол [-π, π]

def is_segment_fully_shadowed_by_angles(A1, A2, B1, B2, S):
    """
    Проверяет, полностью ли отрезок B (B1, B2) покрыт тенью от отрезка A (A1, A2)
    при источнике света S с использованием анализа углов.
    
    Возвращает True, если B полностью в тени.
    """
    # Вычисляем углы для отрезка A
    angle_A1 = angle(A1, S)
    angle_A2 = angle(A2, S)
    
    # Вычисляем углы для отрезка B
    angle_B1 = angle(B1, S)
    angle_B2 = angle(B2, S)
    
    # Определяем минимальный и максимальный углы тени
    min_shadow, max_shadow = sorted([angle_A1, angle_A2])
    min_B, max_B = sorted([angle_B1, angle_B2])
    
    # Если теневая область [min_shadow, max_shadow] полностью накрывает [min_B, max_B], то B в тени
    return min_shadow <= min_B and max_shadow >= max_B

def is_point_inside_polygon(point, polygon):
    """Проверяет, находится ли точка внутри многоугольника (алгоритм Ray-Casting)."""
    x, y = point
    inside = False
    n = len(polygon)
    
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        
        # Проверяем, пересекает ли горизонтальный луч (y) границу многоугольника
        if (y1 > y) != (y2 > y):
            intersect_x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < intersect_x:
                inside = not inside

    return inside

def is_light_inside_shadow_polygon(light, line1, line2):
    """Проверяет, находится ли источник света внутри четырехугольника (ограниченного двумя линиями)."""
    A1, A2 = extend_line_to_bounds(line1[0], line1[1], (-1000, 1000), (-1000, 1000))
    B1, B2 = extend_line_to_bounds(line2[0], line2[1], (-1000, 1000), (-1000, 1000)) 


    # Четырехугольник, образованный двумя линиями
    polygon = [A1, A2, B2, B1]
    
    return is_point_inside_polygon(light, polygon)

def distance(point1, point2):
    """
    Вычисляет евклидово расстояние между двумя точками.

    :param point1: Координаты первой точки (x, y)
    :param point2: Координаты второй точки (x, y)
    :return: Расстояние между точками
    """
    return np.linalg.norm(np.array(point2) - np.array(point1))


def is_same_side_on_segments(seg1_p1, seg1_p2, seg2_p1, seg2_p2, point1, point2):
    """
    Проверяет, находятся ли две точки на одной стороне относительно двух отрезков.
    
    :param seg1_p1, seg1_p2: Концы первого отрезка (tuple (x, y))
    :param seg2_p1, seg2_p2: Концы второго отрезка (tuple (x, y))
    :param point1, point2: Проверяемые точки (tuple (x, y))
    
    :return: True, если обе точки на одной стороне каждого из двух отрезков, иначе False
    """

    def cross_product_sign(a, b, c):
        """Знак векторного произведения AB × AC (определяет, на какой стороне точки b и c от AB)."""
        vec_ab = np.array(b) - np.array(a)
        vec_ac = np.array(c) - np.array(a)
        cross_product = vec_ab[0] * vec_ac[1] - vec_ab[1] * vec_ac[0]
        return np.sign(cross_product)

    # Определяем стороны точек point1 и point2 относительно первого и второго отрезков
    side1_p1 = cross_product_sign(seg1_p1, seg1_p2, point1)
    side1_p2 = cross_product_sign(seg1_p1, seg1_p2, point2)

    side2_p1 = cross_product_sign(seg2_p1, seg2_p2, point1)
    side2_p2 = cross_product_sign(seg2_p1, seg2_p2, point2)

    # Если точки по одну сторону на обоих отрезках, то возвращаем True
    return (side1_p1 == side1_p2 or side1_p1 == 0 or side1_p2 == 0) and (side2_p1 == side2_p2 or side2_p1 == 0 or side2_p2 == 0)

def extend_line_to_bounds(p1, p2, xlim, ylim):
    def intersection_with_bounds(x1, y1, x2, y2, x_bounds, y_bounds):
        points = []
        
        # Проверяем пересечения с вертикальными границами x = x_bounds[0] и x = x_bounds[1]
        if x1 != x2:  # Избегаем деления на 0
            t1 = (x_bounds[0] - x1) / (x2 - x1)
            t2 = (x_bounds[1] - x1) / (x2 - x1)
            y1_int = y1 + t1 * (y2 - y1)
            y2_int = y1 + t2 * (y2 - y1)
            if ylim[0] <= y1_int <= ylim[1]: points.append((x_bounds[0], y1_int))
            if ylim[0] <= y2_int <= ylim[1]: points.append((x_bounds[1], y2_int))

        # Проверяем пересечения с горизонтальными границами y = y_bounds[0] и y = y_bounds[1]
        if y1 != y2:
            t3 = (y_bounds[0] - y1) / (y2 - y1)
            t4 = (y_bounds[1] - y1) / (y2 - y1)
            x3_int = x1 + t3 * (x2 - x1)
            x4_int = x1 + t4 * (x2 - x1)
            if xlim[0] <= x3_int <= xlim[1]: points.append((x3_int, y_bounds[0]))
            if xlim[0] <= x4_int <= xlim[1]: points.append((x4_int, y_bounds[1]))

        return points[:2]  # Должно быть две точки

    points = intersection_with_bounds(p1[0], p1[1], p2[0], p2[1], xlim, ylim)
    
    if len(points) < 2:
        return p1, p2  # На случай ошибок просто возвращаем исходные точки

    return points[0], points[1]

def orientation(p, q, r):
    """
    Определяет ориентацию для тройки точек (p, q, r).
    Возвращает:
    0 если точки коллинеарны,
    1 если поворот по часовой стрелке,
    2 если поворот против часовой стрелки.
    """
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    
    if val == 0:
        return 0  # Коллинеарны
    elif val > 0:
        return 1  # По часовой стрелке
    else:
        return 2  # Против часовой стрелки

def on_segment(p, q, r):
    """
    Проверяет, лежит ли точка q на отрезке pr.
    """
    if min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and min(p[1], r[1]) <= q[1] <= max(p[1], r[1]):
        return True
    return False

def do_intersect(p1, q1, p2, q2):
    """
    Определяет, пересекаются ли два отрезка p1q1 и p2q2.
    """
    # Ориентации для каждой пары точек
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)
    
    # Общий случай: ориентации различаются
    if o1 != o2 and o3 != o4:
        return True
    
    # Специальные случаи:
    # p1, q1 и p2 коллинеарны, проверяем, лежит ли p2 на отрезке p1q1
    if o1 == 0 and on_segment(p1, p2, q1):
        return True
    
    # p1, q1 и p2 коллинеарны, проверяем, лежит ли q2 на отрезке p1q1
    if o2 == 0 and on_segment(p1, q2, q1):
        return True
    
    # p2, q2 и p1 коллинеарны, проверяем, лежит ли p1 на отрезке p2q2
    if o3 == 0 and on_segment(p2, p1, q2):
        return True
    
    # p2, q2 и p1 коллинеарны, проверяем, лежит ли q1 на отрезке p2q2
    if o4 == 0 and on_segment(p2, q1, q2):
        return True
    
    # В остальных случаях отрезки не пересекаются
    return False

def closest_point_on_segment(point, seg_start, seg_end):
    """
    Находит ближайшую точку на отрезке между seg_start и seg_end для точки point.
    
    :param point: Точка, для которой ищем ближайшую точку на отрезке.
    :param seg_start: Начало отрезка.
    :param seg_end: Конец отрезка.
    
    :return: Ближайшая точка на отрезке.
    """
    # Вектор отрезка
    seg_vec = seg_end - seg_start
    # Вектор от точки до начала отрезка
    point_vec = point - seg_start
    # Длина отрезка в квадрате
    seg_len_squared = np.dot(seg_vec, seg_vec)
    
    if seg_len_squared == 0:  # Если отрезок состоит из одной точки
        return seg_start
    
    # Проекция точки на отрезок
    projection = np.dot(point_vec, seg_vec) / seg_len_squared
    # Обрезаем проекцию, чтобы она была в пределах [0, 1]
    projection = np.clip(projection, 0, 1)
    
    # Получаем ближайшую точку
    closest_point = seg_start + projection * seg_vec
    return closest_point


def closest_point_on_segment(point, seg_start, seg_end):
    """
    Находит ближайшую точку на отрезке между seg_start и seg_end для точки point.
    
    :param point: Точка, для которой ищем ближайшую точку на отрезке.
    :param seg_start: Начало отрезка.
    :param seg_end: Конец отрезка.
    
    :return: Ближайшая точка на отрезке.
    """
    # Вектор отрезка
    seg_vec = seg_end - seg_start
    # Вектор от точки до начала отрезка
    point_vec = point - seg_start
    # Длина отрезка в квадрате
    seg_len_squared = np.dot(seg_vec, seg_vec)
    
    if seg_len_squared == 0:  # Если отрезок состоит из одной точки
        return seg_start
    
    # Проекция точки на отрезок
    projection = np.dot(point_vec, seg_vec) / seg_len_squared
    # Обрезаем проекцию, чтобы она была в пределах [0, 1]
    projection = np.clip(projection, 0, 1)
    
    # Получаем ближайшую точку
    closest_point = seg_start + projection * seg_vec
    return closest_point


def is_point_on_segment(p, seg_start, seg_end):
    """Проверяем, находится ли точка p на отрезке между seg_start и seg_end."""
    return min(seg_start[0], seg_end[0]) <= p[0] <= max(seg_start[0], seg_end[0]) and \
           min(seg_start[1], seg_end[1]) <= p[1] <= max(seg_start[1], seg_end[1])

def clip_shadow_line(shadow_line, segment_start, segment_end):
    """Обрезаем линию тени, чтобы она находилась в пределах отрезка."""
    clipped_line = []

    # Для каждой точки тени проверяем, лежит ли она внутри отрезка
    for point in shadow_line:
        if is_point_on_segment(point, segment_start, segment_end):
            clipped_line.append(point)

    # Если точек на отрезке меньше двух, проверяем, где обрезать
    if len(clipped_line) < 2:
        # Если тень выходит за пределы отрезка, то добавляем концы отрезка в точку пересечения
        if is_point_on_segment(segment_start, shadow_line[0], shadow_line[-1]):
            clipped_line.append(segment_start)
        if is_point_on_segment(segment_end, shadow_line[0], shadow_line[-1]):
            clipped_line.append(segment_end)

    if len(clipped_line) < 2:
        return shadow_line
    # Возвращаем обрезанный отрезок
    return clipped_line

def on_ray(p, q, r):
    # Проверка, лежит ли точка q на луче pr (при условии, что q находится на одной стороне от p и r)
    if (r[0] - p[0]) * (q[1] - p[1]) == (r[1] - p[1]) * (q[0] - p[0]):
        return True
    return False

def do_intersect_ray(p1, q1, p2, q2):
    # Определяем ориентацию для 4 комбинаций точек
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)
    
    # Лучи пересекаются, если ориентации разные
    if o1 != o2 and o3 != o4:
        return True
    
    # Специальный случай: если точки на одной линии, то проверяем, лежат ли они на луче
    if o1 == 0 and on_ray(p1, p2, q1):
        return True
    if o2 == 0 and on_ray(p1, q2, q1):
        return True
    if o3 == 0 and on_ray(p2, p1, q2):
        return True
    if o4 == 0 and on_ray(p2, q1, q2):
        return True
    
    return False


def find_closest_points_on_segments(light_pos, intersection_point, segment1_start, segment1_end, segment2_start, segment2_end):
    out = []

    segment1_start_extend, segment1_end_extend = extend_line_to_bounds(segment1_start, segment1_end, plt.xlim(), plt.ylim())
    segment2_start_extend, segment2_end_extend = extend_line_to_bounds(segment2_start, segment2_end, plt.xlim(), plt.ylim())

    if (do_intersect_ray(light_pos, segment1_start, intersection_point, segment2_start_extend) or
        do_intersect_ray(light_pos, segment1_start, intersection_point, segment2_end_extend)):
        out.append(segment1_end)
        out.append(segment1_start)
    else:
        out.append(segment1_start)
        out.append(segment1_end)

    if (do_intersect_ray(light_pos, segment2_start, intersection_point, segment1_start_extend) or
        do_intersect_ray(light_pos, segment2_start, intersection_point, segment1_end_extend)):
        out.append(segment2_end)
        out.append(segment2_start)
    else:
        out.append(segment2_start)
        out.append(segment2_end)

    return out
def shadow_projection(light_pos, p1, p2, q1, q2):
    """Проекция отрезка (p1, p2) на отрезок (q1, q2) для вычисления тени с учетом источника света"""
    
    p1 = np.array(p1)
    p2 = np.array(p2)
    q1 = np.array(q1)
    q2 = np.array(q2)
    light_pos = np.array(light_pos)  # Точка источника света

    # Векторы отрезков
    v1 = p2 - p1
    v2 = q2 - q1

    # Направление света (вектор от источника)
    light_direction = light_pos - p1  # Направление от источника света к точке p1
    
    # Проекционные коэффициенты для каждого конца отрезка p1-p2
    proj_p1 = np.dot(v1, light_direction) / np.dot(light_direction, light_direction)
    proj_p2 = np.dot(v2, light_direction) / np.dot(light_direction, light_direction)
    
    shadow_p1 = p1 + proj_p1 * light_direction
    shadow_p2 = p2 + proj_p2 * light_direction
    
    return shadow_p1.tolist(), shadow_p2.tolist()


class ShadowSimulator:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect('equal', adjustable='datalim')
        self.ax.set_xlim(-100, 100)
        self.ax.set_ylim(-100, 100)
        
        # Линии (заданы набором точек)
        self.line1_points = np.array([[-20, 0], [20, 0]])  # Синяя линия
        self.line2_points = np.array([[-60, -20], [60, -20]])    # Оранжевая линия
        
        # Источник света
        self.light_pos = np.array([0, 40])
        
        # Режим перетаскивания
        self.dragging_point = None
        
        # Рисуем линии и источник
        self.line1, = self.ax.plot(*self.line1_points.T, 'o-', color='red', alpha=0.5)
        self.line2, = self.ax.plot(*self.line2_points.T, 'o-', color='red', alpha=0.5)
        self.light = self.ax.plot(*self.light_pos, 'yo', color='green')[0]
        self.shadow_patch = None

        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)

    def line_intersection(self, p1, p2, q1, q2, segment=False, max_distance=1e6, parallel_threshold=1e-10, A=False, B=False):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = q1
        x4, y4 = q2

        # Вычисляем определитель
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        # Если определитель близок к 0, линии почти параллельны или совпадают
        if abs(denom) < parallel_threshold:
            return None  # Отрезки почти параллельны, пересечения нет

        # Вычисляем координаты точки пересечения
        px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
        py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

        if (A and abs(px) > 100 or abs(py) > 100):
            return None
    
        if B:
            # Определяем направление луча от источника света (p1) к точке (p2)
            direction = np.array(p2, dtype=np.float64) - np.array(p1, dtype=np.float64)
            direction /= np.linalg.norm(direction)  # Нормализуем вектор направления

            # Если луч направлен в положительную сторону по X, ограничиваем до 100
            if direction[0] > 0:
                px = min(px, 100)
            else:
                px = max(px, -100)

            # Если луч направлен в положительную сторону по Y, ограничиваем до 100
            if direction[1] > 0:
                py = min(py, 100)
            else:
                py = max(py, -100)

            return [px, py]


        # Проверяем, что точка пересечения находится в пределах допустимого расстояния
        if px**2 + py**2 > max_distance**2:
            return None  # Точка пересечения слишком далеко

        # Если segment=True, проверяем, лежит ли точка пересечения на отрезках
        if segment:
            # Проверка для первого отрезка
            if not (min(x1, x2) - 1e-10 <= px <= max(x1, x2) + 1e-10 and
                    min(y1, y2) - 1e-10 <= py <= max(y1, y2) + 1e-10):
                return None

            # Проверка для второго отрезка
            if not (min(x3, x4) - 1e-10 <= px <= max(x3, x4) + 1e-10 and
                    min(y3, y4) - 1e-10 <= py <= max(y3, y4) + 1e-10):
                return None

        return [px, py]


    
    def distance_from_point_to_segment(self, point, seg_start, seg_end):
        """
        Находит минимальное расстояние от точки до отрезка.
        """
        seg_vec = seg_end - seg_start
        point_vec = point - seg_start
        seg_len_squared = np.dot(seg_vec, seg_vec)
        if seg_len_squared == 0:
            return np.linalg.norm(point - seg_start)
        projection = np.dot(point_vec, seg_vec) / seg_len_squared
        projection = np.clip(projection, 0, 1)
        closest_point = seg_start + projection * seg_vec
        return np.linalg.norm(point - closest_point)


    def update_shadow(self):
        """
        Обновляет отображение теней.
        """
        # Удаляем старые тени
        for artist in self.ax.lines:
            if artist.get_label() == 'shadow':
                artist.remove()
    
        lines_is_intersect = do_intersect(self.line2_points[0], self.line2_points[1], self.line1_points[0],  self.line1_points[1])
        closer_line_points, farther_line_points = determine_shadow_caster(self.light_pos, self.line1_points, self.line2_points)
        print(closer_line_points, farther_line_points)
        
        shadow_lines = []
        
        if lines_is_intersect:
            intersection_point = self.line_intersection(self.line1_points[0], self.line1_points[1], self.line2_points[0], self.line2_points[1])
            closest_point_line_1, dalnia_1, closest_point_line_2, dalnia_2 = find_closest_points_on_segments(self.light_pos, intersection_point,  self.line1_points[0], self.line1_points[1], self.line2_points[0], self.line2_points[1])

            shadow_points1 = [intersection_point]
            shadow_point = self.line_intersection(self.light_pos, closest_point_line_1, self.line2_points[0], self.line2_points[1], A=True)
            if shadow_point is None:
                shadow_points1.append([dalnia_2[0], dalnia_2[1]])
            elif is_same_side_on_segments(intersection_point, closest_point_line_2, intersection_point, closest_point_line_1, shadow_point, self.light_pos):
                shadow_points1.append([dalnia_2[0], dalnia_2[1]])
            else:
                shadow_points1.append(shadow_point)
            if len(shadow_points1) == 2:
                clipped_shadow1 = clip_shadow_line(shadow_points1, self.line2_points[0], self.line2_points[1])
                shadow_lines.append(clipped_shadow1)

            shadow_points2 = [intersection_point]
            shadow_point = self.line_intersection(self.light_pos, closest_point_line_2, self.line1_points[0], self.line1_points[1], A=True)
            if shadow_point is None:
                shadow_points2.append([dalnia_1[0], dalnia_1[1]])
            elif is_same_side_on_segments(intersection_point, closest_point_line_2, intersection_point, closest_point_line_1, shadow_point, self.light_pos):
                shadow_points2.append([dalnia_1[0], dalnia_1[1]])
            else:
                shadow_points2.append(shadow_point)
            if len(shadow_points2) == 2:
                clipped_shadow2 = clip_shadow_line(shadow_points2, self.line1_points[0], self.line1_points[1])
                shadow_lines.append(clipped_shadow2)
        else:
            shadow_points= []

            if is_shadow_cast(self.line1_points, self.line2_points, self.light_pos):
                print("shadow cast")
                self.fig.canvas.draw_idle()
                return

            
            if is_segment_fully_shadowed_by_angles(self.line1_points[0], self.line1_points[1], self.line2_points[0], self.line2_points[1], self.light_pos):
                shadow_points = [farther_line_points[0], farther_line_points[1]]
            else:
                for point in closer_line_points:
                    shadow_point = self.line_intersection(self.light_pos, point, farther_line_points[0], farther_line_points[1], B=True)

                    print(2, shadow_point)
                    if shadow_point is None:
                        # Определяем, какой конец дальнего отрезка "дальше" от источника света
                        dist1 = distance(point, farther_line_points[0])
                        dist2 = distance(point, farther_line_points[1])
                        if dist1 < dist2:
                            shadow_point = farther_line_points[1]
                        else:
                            shadow_point = farther_line_points[0]

                    clipped_point = closest_point_on_segment(shadow_point, farther_line_points[0], farther_line_points[1])
                    shadow_points.append(clipped_point)
            print(1, shadow_points)
            if len(shadow_points) == 2:
                shadow_lines.append(shadow_points)

        for shadow_points in shadow_lines:
            shadow_line = Line2D([shadow_points[0][0], shadow_points[1][0]],
                                [shadow_points[0][1], shadow_points[1][1]], 
                                color='black', label='shadow')
            self.ax.add_line(shadow_line)

        # Обновление канваса
        self.fig.canvas.draw_idle()

    def on_press(self, event):
        if event.inaxes != self.ax:
            return

        # Проверяем, выбрана ли точка для перемещения
        for idx, point in enumerate(self.line1_points):
            if np.linalg.norm(point - [event.xdata, event.ydata]) < 10:
                self.dragging_point = ('line1', idx)
                return
        for idx, point in enumerate(self.line2_points):
            if np.linalg.norm(point - [event.xdata, event.ydata]) < 10:
                self.dragging_point = ('line2', idx)
                return
        if np.linalg.norm(self.light_pos - [event.xdata, event.ydata]) < 10:
            self.dragging_point = 'light'

    def on_drag(self, event):
        if self.dragging_point is None or event.inaxes != self.ax:
            return
        
        if self.dragging_point == 'light':
            self.light_pos[:] = [event.xdata, event.ydata]
            self.light.set_data(*self.light_pos)
        else:
            line, idx = self.dragging_point
            if line == 'line1':
                self.line1_points[idx] = [event.xdata, event.ydata]
                self.line1.set_data(*self.line1_points.T)
            elif line == 'line2':
                self.line2_points[idx] = [event.xdata, event.ydata]
                self.line2.set_data(*self.line2_points.T)
        
        self.update_shadow()

    def on_release(self, event):
        self.dragging_point = None

    def run(self):
        self.update_shadow()
        plt.show()


if __name__ == "__main__":
    sim = ShadowSimulator()
    sim.run()


