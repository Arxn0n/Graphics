import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Функция для вычисления биномиального коэффициента
def binomial_coeff(n, k):
    if k == 0 or k == n:
        return 1
    return binomial_coeff(n - 1, k - 1) + binomial_coeff(n - 1, k)

# Функция для вычисления точки на кривой Безье
def bezier_point(t, control_points):
    n = len(control_points) - 1
    x, y = 0, 0
    for i, (px, py) in enumerate(control_points):
        coeff = binomial_coeff(n, i) * (1 - t)**(n - i) * t**i
        x += coeff * px
        y += coeff * py
    return x, y

# Построение кривой Безье
def bezier_curve(control_points, steps=1000):
    curve = [bezier_point(t, control_points) for t in np.linspace(0, 1, steps)]
    return zip(*curve)

# Функция отрисовки графика
def draw_graph():
    ax.clear()
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    
    # Рисуем все линии Безье
    for line_idx, (control_points, color, label) in enumerate(lines):
        if len(control_points) >= 2:
            x, y = bezier_curve(control_points)
            ax.plot(x, y, color=color, label=f"Линия {label}")  # Кривая Безье
            ax.plot(*zip(*control_points), linestyle="--", color="gray")  # Направляющие линии

        # Рисуем точки с их метками
        for point_idx, (px, py) in enumerate(control_points):
            ax.scatter(px, py, color=color)
            ax.text(px + 0.2, py, f"{label}{point_idx + 1}", fontsize=9, color=color)

    ax.legend()
    ax.grid(True)
    canvas.draw()

# Проверка, находится ли курсор в пределах точки
def is_near_point(event, px, py, threshold=0.5):
    return abs(event.xdata - px) < threshold and abs(event.ydata - py) < threshold

# Добавление или выбор точки на ЛКМ
def on_left_click(event):
    global selected_point_index, selected_line_index
    if not event.inaxes:
        return

    x, y = event.xdata, event.ydata

    # Проверяем, попал ли пользователь в существующую точку
    for line_idx, (control_points, _, _) in enumerate(lines):
        for point_idx, (px, py) in enumerate(control_points):
            if is_near_point(event, px, py):
                selected_line_index = line_idx
                selected_point_index = point_idx
                return
    def insert_point_between(event):
        global lines
        if not event.inaxes:
            return
    x, y = event.xdata, event.ydata

    for line_idx, (control_points, _, _) in enumerate(lines):
        if len(control_points) < 2:
            continue

        for i in range(len(control_points) - 1):
            px1, py1 = control_points[i]
            px2, py2 = control_points[i + 1]
            
            # Найдите среднюю точку
            mid_x, mid_y = (px1 + px2) / 2, (py1 + py2) / 2
            if abs(x - mid_x) < 0.5 and abs(y - mid_y) < 0.5:
                control_points.insert(i + 1, (x, y))
                draw_graph()
                return


    # Если клик не на существующей точке, добавляем новую
    if selected_line_index is None:
        selected_line_index = len(lines) - 1  # Выбираем последнюю линию по умолчанию
    lines[selected_line_index][0].append((x, y))
    selected_point_index = None
    draw_graph()


# Удаление точки по правому клику мыши
def on_right_click(event):
    global lines
    if not event.inaxes:
        return

    x, y = event.xdata, event.ydata

    # Поиск точки для удаления
    for line_idx, (control_points, _, _) in enumerate(lines):
        for point_idx, (px, py) in enumerate(control_points):
            if is_near_point(event, px, py):
                # Удаляем точку
                del control_points[point_idx]
                draw_graph()
                return

# Обновление позиции выбранной точки
def on_mouse_motion(event):
    global selected_point_index, selected_line_index
    if selected_point_index is not None and selected_line_index is not None and event.inaxes:
        lines[selected_line_index][0][selected_point_index] = (event.xdata, event.ydata)
        draw_graph()

# Сброс выделения точки при отпускании мыши
def on_mouse_release(event):
    global selected_point_index, selected_line_index
    selected_point_index = None
    selected_line_index = None

# Очистка графика
def clear_graph():
    global lines, selected_line_index
    lines = [[[], "red", "A"]]  # Оставляем первую линию
    selected_line_index = 0
    draw_graph()

# Добавление новой линии
def add_new_line():
    global lines, selected_line_index
    new_label = chr(ord(lines[-1][2]) + 1)  # Новая буква (A -> B -> C)
    new_color = np.random.rand(3,)  # Генерация случайного цвета
    lines.append([[], new_color, new_label])
    selected_line_index = len(lines) - 1
    draw_graph()

def show_instructions():
    instructions = (
        "Инструкция по управлению:\n"
        "1. Левая кнопка мыши на пустом месте - добавление новой точки в текущую линию.\n"
        "2. Левая кнопка мыши на точке - выбор точки для перетаскивания.\n"
        "3. Перемещение мыши с зажатой ЛКМ на выбранной точке - перетаскивание точки.\n"
        "4. Пунктирные линии - направляющие линии между точками.\n"
        "5. Синяя линия - построенная кривая Безье.\n"
        "6. Кнопка 'Стереть все' - удаляет все линии и точки.\n"
        "7. Клик ЛКМ между двумя точками линии - добавление новой точки между ними.\n"
        "8. Правый клик мыши на точке - удаление узла.\n"
        "9. Кнопки '+' и '-' - изменение масштаба графика."
    )
    messagebox.showinfo("Инструкция", instructions)


# Функция для изменения масштаба
def zoom(scale):
    global x_min, x_max, y_min, y_max
    x_center = (x_max + x_min) / 2
    y_center = (y_max + y_min) / 2
    x_range = (x_max - x_min) * scale
    y_range = (y_max - y_min) * scale
    x_min, x_max = x_center - x_range / 2, x_center + x_range / 2
    y_min, y_max = y_center - y_range / 2, y_center + y_range / 2
    draw_graph()

# Основная программа
root = tk.Tk()
root.title("Интерактивное построение линий Безье")

# Глобальные переменные
lines = [[[], "blue", "A"]]  # Список линий (точки, цвет, метка)
selected_line_index = 0
selected_point_index = None

# Статичные границы графика
x_min, x_max = -10, 10
y_min, y_max = -10, 10

# Левый фрейм с кнопками
frame_left = tk.Frame(root)
frame_left.pack(side=tk.LEFT, padx=10, pady=10)

tk.Button(frame_left, text="Инструкция", command=show_instructions).pack(pady=5)
tk.Button(frame_left, text="Стереть все", command=clear_graph).pack(pady=5)
tk.Button(frame_left, text="Увеличить (+)", command=lambda: zoom(0.8)).pack(pady=5)
tk.Button(frame_left, text="Уменьшить (-)", command=lambda: zoom(1.2)).pack(pady=5)

# График Matplotlib
fig, ax = plt.subplots(figsize=(6, 6))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Привязка событий
# Привязка событий
canvas.mpl_connect("button_press_event", on_left_click)  # Добавление или выбор точки
canvas.mpl_connect("motion_notify_event", on_mouse_motion)  # Перетаскивание точки
canvas.mpl_connect("button_release_event", on_mouse_release)  # Сброс выбора точки
canvas.mpl_connect("button_press_event", lambda event: on_right_click(event) if event.button == 3 else None)  # Удаление точки


# Инициализация графика
draw_graph()

root.mainloop()
