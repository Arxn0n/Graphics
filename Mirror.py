import pygame
import math

# Инициализация Pygame
pygame.init()

# Определение размеров окна
width, height = 600, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Перетаскивание источника света с отражением луча")

# Определение цветов
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Параметры зеркала (две перпендикулярные грани)
mirror_size = 200

# Сдвигаем зеркало правее, добавив 200 пикселей
mirror_x = width // 2 + 200  # смещение вправо на 200 пикселей
mirror_y = height // 2  # центр по вертикали

# Источник света (начальная позиция)
light_x, light_y = 100, 100
dragging = False  # Флаг, который отслеживает, перетаскивается ли источник света

# Стабильная позиция луча
stable_ray = None  # Переменная для хранения стабильной позиции луча

# Функция для рисования зеркала, повернутого на 90 градусов
def draw_mirror():
    # Первая грань зеркала (угол 135 градусов от горизонтали)
    x1 = mirror_x
    y1 = mirror_y
    x2 = x1 + mirror_size * math.cos(math.radians(135))  # угол 135 градусов
    y2 = y1 + mirror_size * math.sin(math.radians(135))
    
    # Вторая грань зеркала (угол 225 градусов от горизонтали)
    x3 = x1 + mirror_size * math.cos(math.radians(225))  # угол 225 градусов
    y3 = y1 + mirror_size * math.sin(math.radians(225))
    
    # Рисуем две линии (гранями зеркала)
    pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), 2)  # Первая грань зеркала
    pygame.draw.line(screen, BLACK, (x1, y1), (x3, y3), 2)  # Вторая грань зеркала

# Функция для рисования источника света (красный круг)
def draw_light_source():
    pygame.draw.circle(screen, RED, (light_x, light_y), 5)  # рисуем источник света

# Функция для рисования луча света
def draw_light_ray():
    global stable_ray
    # Если луч стабилизирован (нажата ПКМ), рисуем его с фиксированным концом
    if stable_ray:
        # Сначала рисуем луч
        pygame.draw.line(screen, RED, (light_x, light_y), stable_ray, 2)  # красный луч
        # Проверка на пересечение луча с зеркалом и отражение
        reflect_ray(stable_ray)
    else:
        # Если луч не стабилизирован, рисуем его от источника до позиции мыши
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.line(screen, RED, (light_x, light_y), (mouse_x, mouse_y), 2)  # красный луч

# Функция для вычисления пересечения луча с зеркалом
def line_intersection(p1, p2, q1, q2):
    # p1, p2 - конец луча, q1, q2 - грань зеркала
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = q1
    x4, y4 = q2

    # Расчет детерминанта для нахождения пересечения
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None  # если пересечение невозможно (параллельны)

    intersect_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    intersect_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

    return (intersect_x, intersect_y)

# Функция для вычисления отражения луча
def reflect_ray(ray_end):
    # Математика для отражения луча
    # Расчет угла падения и угла отражения
    mirror_x1 = mirror_x
    mirror_y1 = mirror_y
    mirror_x2 = mirror_x + mirror_size * math.cos(math.radians(135))
    mirror_y2 = mirror_y + mirror_size * math.sin(math.radians(135))

    # Находим точку пересечения луча с зеркалом
    intersection = line_intersection((light_x, light_y), ray_end, (mirror_x1, mirror_y1), (mirror_x2, mirror_y2))
    if intersection:
        # Расчитаем нормаль
        norm_x = mirror_x2 - mirror_x1
        norm_y = mirror_y2 - mirror_y1
        norm_len = math.sqrt(norm_x ** 2 + norm_y ** 2)
        norm_x /= norm_len
        norm_y /= norm_len

        # Вектор луча от источника до точки пересечения
        ray_dx = intersection[0] - light_x
        ray_dy = intersection[1] - light_y

        # Нормализуем вектор падения
        ray_len = math.sqrt(ray_dx ** 2 + ray_dy ** 2)
        ray_dx /= ray_len
        ray_dy /= ray_len

        # Находим угол отражения
        dot_product = ray_dx * norm_x + ray_dy * norm_y
        reflection_dx = ray_dx - 2 * dot_product * norm_x
        reflection_dy = ray_dy - 2 * dot_product * norm_y

        # Рисуем отраженный луч
        reflected_end_x = intersection[0] + reflection_dx * 100
        reflected_end_y = intersection[1] + reflection_dy * 100
        pygame.draw.line(screen, RED, intersection, (reflected_end_x, reflected_end_y), 2)

# Основной цикл программы
running = True
while running:
    screen.fill(WHITE)  # очищаем экран

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Обрабатываем событие нажатия ЛКМ (перетаскивание источника света)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # левая кнопка мыши
                # Проверяем, находится ли курсор внутри источника света
                if (light_x - event.pos[0]) ** 2 + (light_y - event.pos[1]) ** 2 <= 25:
                    dragging = True  # начинаем перетаскивание
            elif event.button == 3:  # правая кнопка мыши
                # Фиксируем позицию луча
                stable_ray = pygame.mouse.get_pos()  # сохраняем текущую позицию мыши

        # Обрабатываем событие отпускания ЛКМ
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # левая кнопка мыши
                dragging = False  # заканчиваем перетаскивание

        # Перетаскивание источника света
        elif event.type == pygame.MOUSEMOTION:
            if dragging:  # если перетаскиваем
                light_x, light_y = event.pos  # обновляем позицию источника света

    # Рисуем зеркало
    draw_mirror()

    # Рисуем источник света
    draw_light_source()

    # Рисуем луч света
    draw_light_ray()

    pygame.display.flip()  # обновляем экран

pygame.quit()
