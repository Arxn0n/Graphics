import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ParametricShapesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Параметрические фигуры")

        # Параметры по умолчанию
        self.shape = "ellipse"
        self.default_a, self.default_b = 5, 3
        self.a, self.b = self.default_a, self.default_b
        self.angle = 0
        self.offset_x, self.offset_y = 0, 0
        self.dragging = False  # Флаг для перемещения

        # Интерфейс
        self.create_widgets()
        self.plot_shape()

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Выбор фигуры
        tk.Label(frame, text="Фигура:").pack()
        self.shape_var = tk.StringVar(value="ellipse")
        shapes = [
            ("Эллипс", "ellipse"),
            ("Парабола", "parabola"),
            ("Гипербола", "hyperbola"),
            ("Кардиоида", "cardioid"),
            ("Роза", "rose"),
            ("Гиперолическая спираль", "bernoulli_spiral"),
            ("Пила", "custom"),
              ("Модифицированная спираль", "modified_spiral")   # Новый пункт
            ]


        for text, value in shapes:
            tk.Radiobutton(frame, text=text, variable=self.shape_var, value=value, command=self.plot_shape).pack()

        # Параметры через слайдеры
        tk.Label(frame, text="a:").pack()
        self.a_slider = tk.Scale(frame, from_=1, to=20, orient="horizontal", command=self.update_plot)
        self.a_slider.set(self.default_a)
        self.a_slider.pack()

        tk.Label(frame, text="b:").pack()
        self.b_slider = tk.Scale(frame, from_=1, to=20, orient="horizontal", command=self.update_plot)
        self.b_slider.set(self.default_b)
        self.b_slider.pack()

        tk.Label(frame, text="Угол (градусы):").pack()
        self.angle_slider = tk.Scale(frame, from_=0, to=360, orient="horizontal", command=self.update_plot)
        self.angle_slider.set(0)
        self.angle_slider.pack()

        tk.Label(frame, text="Смещение по X:").pack()
        self.offset_x_slider = tk.Scale(frame, from_=-20, to=20, orient="horizontal", command=self.update_plot)
        self.offset_x_slider.set(0)
        self.offset_x_slider.pack()

        tk.Label(frame, text="Смещение по Y:").pack()
        self.offset_y_slider = tk.Scale(frame, from_=-20, to=20, orient="horizontal", command=self.update_plot)
        self.offset_y_slider.set(0)
        self.offset_y_slider.pack()

        # График
        self.fig, self.ax = plt.subplots(figsize=(5, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Обработчик событий мыши
        self.canvas.mpl_connect("button_press_event", self.on_mouse_press)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_drag)
        self.canvas.mpl_connect("button_release_event", self.on_mouse_release)

    def update_plot(self, event=None):
        self.a = self.a_slider.get()
        self.b = self.b_slider.get()
        self.angle = np.radians(self.angle_slider.get())
        self.offset_x = self.offset_x_slider.get()
        self.offset_y = self.offset_y_slider.get()
        self.plot_shape()

    def plot_shape(self):
        self.ax.clear()
        shape = self.shape_var.get()

        # Определение фигуры
        if shape == "ellipse":
            t = np.linspace(0, 2 * np.pi, 500)
            x = self.a * np.cos(t)
            y = self.b * np.sin(t)
        elif shape == "parabola":
            t = np.linspace(-10, 10, 500)
            x = self.a * t
            y = self.b * t**2
        elif shape == "hyperbola":
            t = np.linspace(-3, 3, 500)
            x1 = self.a * np.cosh(t)
            y1 = self.b * np.sinh(t)
            x2 = -self.a * np.cosh(t)
            y2 = self.b * np.sinh(t)

   
            x1_rot, y1_rot = self.transform(x1, y1)
            x2_rot, y2_rot = self.transform(x2, y2)

    
            self.ax.plot(x1_rot, y1_rot, color="Green", label="Гипербола (ветвь 1)")
            self.ax.plot(x2_rot, y2_rot, color="blue", label="Гипербола (ветвь 2)")
            self.ax.legend()
            self.ax.set_xlim(-20, 20)
            self.ax.set_ylim(-20, 20)
            self.ax.grid(True)
            self.canvas.draw()
            return  # Завершаем выполнение функции, так как график уже построен

        elif shape == "cardioid":
            t = np.linspace(0, 2 * np.pi, 500)
            r = self.a * (1 + self.b * np.cos(t))
            x = r * np.cos(t)
            y = r * np.sin(t)

        elif shape == "rose":
            t = np.linspace(0, 2 * np.pi, 500)
            r = self.a * np.cos(self.b * t)
            x = r * np.cos(t)
            y = r * np.sin(t)
        elif shape == "bernoulli_spiral":
            t = np.linspace(0.01, 10, 500)  # Угол θ от 0.01 (исключаем деление на ноль) до 10
            r = self.a / np.sqrt(1 + self.b**2 * t**2)  # Уравнение спирали Бернулли
            x = r * np.cos(t)  # Перевод в декартовы координаты
            y = r * np.sin(t)
        elif shape == "custom":  # Новая фигура
            t = np.linspace(0, 4 * np.pi, 500)  # Диапазон t
            r = self.a * (2 - np.mod(t, np.pi / 3))  # r(t) с влиянием параметра a
            phi = t + self.b * np.mod(t, np.pi / 12)  # φ(t) с влиянием параметра b
            x = r * np.cos(phi)
            y = r * np.sin(phi)
        elif shape == "modified_spiral":  # Новая фигура
            t = np.linspace(0, 4 * np.pi, 500)  # Диапазон t
            r = self.a * (2 + np.cos(10 * t))  # Масштабируемая функция радиуса
            phi = t + self.b * 0.5 * np.sin(10 * t)**2  # Угловая функция с параметром b
            x = r * np.cos(phi)
            y = r * np.sin(phi)



        # Трансформация
        x_rot, y_rot = self.transform(x, y)

        # Построение графика
        self.ax.plot(x_rot, y_rot, label=shape, color="green")
        self.ax.legend()
        self.ax.set_xlim(-20, 20)
        self.ax.set_ylim(-20, 20)
        self.ax.grid(True)
        self.canvas.draw()

    def transform(self, x, y):
        x_rot = x * np.cos(self.angle) - y * np.sin(self.angle) + self.offset_x
        y_rot = x * np.sin(self.angle) + y * np.cos(self.angle) + self.offset_y
        return x_rot, y_rot

    def on_mouse_press(self, event):
        if event.xdata is not None and event.ydata is not None:
            self.dragging = True
            self.prev_mouse_x = event.xdata
            self.prev_mouse_y = event.ydata

    def on_mouse_drag(self, event):
        if self.dragging and event.xdata is not None and event.ydata is not None:
            dx = event.xdata - self.prev_mouse_x
            dy = event.ydata - self.prev_mouse_y
            self.offset_x += dx
            self.offset_y += dy
            self.prev_mouse_x = event.xdata
            self.prev_mouse_y = event.ydata
            self.update_plot()

    def on_mouse_release(self, event):
        self.dragging = False

    def reset(self):
        self.a_slider.set(self.default_a)
        self.b_slider.set(self.default_b)
        self.angle_slider.set(0)
        self.offset_x_slider.set(0)
        self.offset_y_slider.set(0)
        self.plot_shape()

# Запуск приложения
root = tk.Tk()
app = ParametricShapesApp(root)
root.mainloop()
