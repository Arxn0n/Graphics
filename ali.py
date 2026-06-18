import pygame
import math
import sys

pygame.init()
WIDTH, HEIGHT = 920, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Уголковый катафот — зигзагообразное зеркало со слайдерами")

clock = pygame.time.Clock()

# Начальные параметры
mirror_center = [WIDTH // 2, HEIGHT // 2]
mirror_angle = 180
mirror_length = 150
mirror_count = 10
mirror_rotation = 0
rays = []
adding_ray = False
temp_ray_start = None
editing_mode = False
dragging_ray = None
dragging_end = False

# Цвета
colors = [(255, 0, 0), (0, 255, 0), (0, 200, 255), (255, 255, 0), (255, 0, 255), (255, 128, 0)]
font = pygame.font.SysFont("Arial", 20)

def normalize(v):
    length = math.hypot(v[0], v[1])
    return [v[0]/length, v[1]/length] if length != 0 else [0, 0]

def dot(a, b):
    return a[0]*b[0] + a[1]*b[1]

def reflect(direction, normal):
    d_dot_n = dot(direction, normal)
    return [
        direction[0] - 2 * d_dot_n * normal[0],
        direction[1] - 2 * d_dot_n * normal[1]
    ]

def rotate_point(px, py, cx, cy, angle_rad):
    s, c = math.sin(angle_rad), math.cos(angle_rad)
    px -= cx
    py -= cy
    xnew = px * c - py * s
    ynew = px * s + py * c
    return [xnew + cx, ynew + cy]

def create_mirror_chain(center, angle_deg, count, rotation_deg):
    mirrors = []
    angle_rad = math.radians(angle_deg / 2)
    dx = math.cos(angle_rad) * mirror_length
    dy = math.sin(angle_rad) * mirror_length
    direction = 1
    start = [center[0] - count * dx / 2, center[1]]
    rot_rad = math.radians(rotation_deg)

    for _ in range(count):
        end = [start[0] + dx, start[1] + direction * dy]
        r_start = rotate_point(*start, *center, rot_rad)
        r_end = rotate_point(*end, *center, rot_rad)
        mirrors.append((r_start, r_end))
        start = end
        direction *= -1

    return mirrors

def get_normal(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    return normalize([dy, -dx])

def draw_segment(p1, p2, color=(255, 255, 0)):
    pygame.draw.line(screen, color, p1, p2, 2)

def segment_intersect(p, d, seg_a, seg_b):
    v1 = [p[0] - seg_a[0], p[1] - seg_a[1]]
    v2 = [seg_b[0] - seg_a[0], seg_b[1] - seg_a[1]]
    v3 = [-d[1], d[0]]
    denom = dot(v2, v3)

    if abs(denom) < 1e-6:
        return None

    t1 = (v2[0]*v1[1] - v2[1]*v1[0]) / denom
    t2 = dot(v1, v3) / denom

    if 0 <= t2 <= 1 and t1 >= 0:
        return [p[0] + t1*d[0], p[1] + t1*d[1]]
    return None

def process_ray(ray_start, ray_dir, mirrors, color):
    max_reflections = 8
    current_point = ray_start[:]
    direction = ray_dir[:]

    for _ in range(max_reflections):
        intersections = []
        for mirror in mirrors:
            hit = segment_intersect(current_point, direction, mirror[0], mirror[1])
            if hit:
                dist = math.hypot(hit[0] - current_point[0], hit[1] - current_point[1])
                intersections.append((dist, hit, mirror))

        if not intersections:
            end = [current_point[0] + direction[0] * 1000, current_point[1] + direction[1] * 1000]
            draw_segment(current_point, end, color)
            break

        intersections.sort(key=lambda x: x[0])
        _, hit_point, mirror = intersections[0]
        draw_segment(current_point, hit_point, color)
        direction = reflect(direction, get_normal(mirror[0], mirror[1]))
        current_point = [hit_point[0] + direction[0] * 0.1, hit_point[1] + direction[1] * 0.1]

# UI Элементы
class Slider:
    def __init__(self, x, y, w, min_val, max_val, start_val, label):
        self.rect = pygame.Rect(x, y, w, 30)
        self.min = min_val
        self.max = max_val
        self.val = start_val
        self.dragging = False
        self.label = label
        self.inc_btn = pygame.Rect(x + w + 10, y, 30, 30)
        self.dec_btn = pygame.Rect(x - 40, y, 30, 30)

    def draw(self, surf):
        pygame.draw.rect(surf, (100, 100, 100), self.rect)
        knob_x = self.rect.x + (self.val - self.min) / (self.max - self.min) * self.rect.w
        pygame.draw.circle(surf, (220, 220, 220), (int(knob_x), self.rect.y + 15), 10)
        text = font.render(f"{self.label}: {int(self.val)}", True, (255, 255, 255))
        surf.blit(text, (self.rect.x, self.rect.y - 25))
        pygame.draw.rect(surf, (180, 180, 180), self.inc_btn)
        pygame.draw.rect(surf, (180, 180, 180), self.dec_btn)
        surf.blit(font.render("+", True, (0, 0, 0)), (self.inc_btn.x + 8, self.inc_btn.y + 5))
        surf.blit(font.render("-", True, (0, 0, 0)), (self.dec_btn.x + 10, self.dec_btn.y + 5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
            elif self.inc_btn.collidepoint(event.pos):
                self.val = min(self.val + 1, self.max)
            elif self.dec_btn.collidepoint(event.pos):
                self.val = max(self.val - 1, self.min)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.rect.x
            rel_x = max(0, min(rel_x, self.rect.w))
            self.val = self.min + (rel_x / self.rect.w) * (self.max - self.min)

    def get_value(self):
        return self.val

sliders = [
    Slider(50, 50, 300, 0, 360, mirror_angle, "Угол зеркала"),
    Slider(50, 100, 300, 10, 300, mirror_length, "Длина грани"),
    Slider(50, 150, 300, 1, 100, mirror_count, "Количество"),
    Slider(50, 200, 300, 0, 360, mirror_rotation, "Вращение")
]

edit_button = pygame.Rect(50, 250, 160, 40)
instruction_button = pygame.Rect(WIDTH - 160, 10, 150, 40)
instruction_text = font.render("Инструкция", True, (255, 255, 255))

instructions = [
    "ЛКМ по началу луча — перетаскивание.",
    "ЛКМ по концу луча — изменить направление.",
    "ПКМ (дважды) — добавить луч.",
    "'~' — удалить последний луч.",
    "Слайдеры — настроить зеркало.",
    "Кнопка 'Редактирование' — включить удаление лучей ПКМ."
]

def draw_instructions():
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(300, 100, 500, 300))
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(300, 100, 500, 300), 3)
    for i, line in enumerate(instructions):
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (320, 120 + i * 30))

show_instructions = False

# Главный цикл
running = True
while running:
    screen.fill((0, 0, 0))
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        for slider in sliders:
            slider.handle_event(event)

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKQUOTE and rays:
                rays.pop()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if edit_button.collidepoint(event.pos):
                editing_mode = not editing_mode

            elif instruction_button.collidepoint(event.pos):
                show_instructions = not show_instructions

            elif editing_mode and event.button == 3:
                for i, (start, direction) in enumerate(rays):
                    if math.hypot(start[0] - mouse_pos[0], start[1] - mouse_pos[1]) < 10:
                        rays.pop(i)
                        break
            elif event.button == 3:
                if not adding_ray:
                    temp_ray_start = mouse_pos
                    adding_ray = True
                else:
                    dir_vec = normalize([mouse_pos[0] - temp_ray_start[0], mouse_pos[1] - temp_ray_start[1]])
                    rays.append((temp_ray_start, dir_vec))
                    adding_ray = False
                    temp_ray_start = None
            elif event.button == 1:
                for i, (start, direction) in enumerate(rays):
                    end = [start[0] + direction[0]*100, start[1] + direction[1]*100]
                    if math.hypot(mouse_pos[0] - start[0], mouse_pos[1] - start[1]) < 10:
                        dragging_ray = i
                        dragging_end = False
                        break
                    elif math.hypot(mouse_pos[0] - end[0], mouse_pos[1] - end[1]) < 10:
                        dragging_ray = i
                        dragging_end = True
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_ray = None
            dragging_end = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging_ray is not None:
                if dragging_end:
                    start = rays[dragging_ray][0]
                    dx = mouse_pos[0] - start[0]
                    dy = mouse_pos[1] - start[1]
                    direction = normalize([dx, dy])
                    rays[dragging_ray] = (start, direction)
                else:
                    direction = rays[dragging_ray][1]
                    rays[dragging_ray] = (mouse_pos, direction)

    # Слайдеры
    mirror_angle = sliders[0].get_value()
    mirror_length = sliders[1].get_value()
    mirror_count = int(sliders[2].get_value())
    mirror_rotation = sliders[3].get_value()
    mirrors = create_mirror_chain(mirror_center, mirror_angle, mirror_count, mirror_rotation)

    for m in mirrors:
        pygame.draw.line(screen, (255, 255, 255), m[0], m[1], 3)

        for i, (start, direction) in enumerate(rays):
            process_ray(start, direction, mirrors, colors[i % len(colors)])

        # Добавляем кружки на начальную и направляющую точки луча
            end = [start[0] + direction[0]*100, start[1] + direction[1]*100]
            pygame.draw.circle(screen, (255, 255, 255), (int(start[0]), int(start[1])), 6, 2)
            pygame.draw.circle(screen, (255, 255, 255), (int(end[0]), int(end[1])), 6, 2)


    if adding_ray and temp_ray_start:
        pygame.draw.line(screen, (100, 100, 100), temp_ray_start, mouse_pos, 1)

    for s in sliders:
        s.draw(screen)

    pygame.draw.rect(screen, (0, 255, 0) if editing_mode else (255, 0, 0), edit_button)
    screen.blit(font.render("Редактирование", True, (0, 0, 0)), (edit_button.x + 10, edit_button.y + 10))
    pygame.draw.rect(screen, (0, 0, 255), instruction_button)
    screen.blit(instruction_text, (instruction_button.x + 10, instruction_button.y + 10))

    if show_instructions:
        draw_instructions()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
