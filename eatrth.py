import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

# Параметры
orbit_radius = 30
tilt_angle = np.radians(23.5)
earth_radius = 6
axis_length = earth_radius * 4
total_frames = 360
earth_rotations = 8
num_meridians = 12

# Фигура
fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(111, projection='3d')
view_range = orbit_radius + 30
ax.set_xlim([-view_range, view_range])
ax.set_ylim([-view_range, view_range])
ax.set_zlim([-view_range / 2, view_range / 2])
ax.set_box_aspect([1, 1, 0.5])
ax.grid(False)
ax.set_axis_off()
fig.patch.set_facecolor('black')
ax.set_facecolor('black')

# Орбита
theta = np.linspace(0, 2 * np.pi, 360)
orbit_x = orbit_radius * np.cos(theta)
orbit_y = orbit_radius * np.sin(theta)
orbit_z = np.zeros_like(theta)
ax.plot(orbit_x, orbit_y, orbit_z, color='green', linestyle='--', linewidth=1.5)

# Солнце
ax.plot([0], [0], [0], marker='o', markersize=50, color='yellow')

# Земля-сфера
earth_surface = None

# Ось вращения Земли
earth_axis_line, = ax.plot([], [], [], color='red', linewidth=2)
earth_pole_line, = ax.plot([], [], [], color='cyan', linewidth=2)

# Меридианы
meridian_lines = []
for i in range(num_meridians):
    phi = 2 * np.pi * i / num_meridians
    color = 'yellow' if i == 0 else 'white'
    line, = ax.plot([], [], [], color=color, linewidth=3)
    meridian_lines.append((phi, line))

# Сетка сферы
u, v = np.mgrid[0:2 * np.pi:40j, 0:np.pi:20j]
x0 = earth_radius * np.cos(u) * np.sin(v)
y0 = earth_radius * np.sin(u) * np.sin(v)
z0 = earth_radius * np.cos(v)

# Вращение вокруг оси X (наклон Земли)
Rx_tilt = np.array([
    [1, 0, 0],
    [0, np.cos(tilt_angle), -np.sin(tilt_angle)],
    [0, np.sin(tilt_angle), np.cos(tilt_angle)]
])

# Функция обновления
def update(frame):
    global earth_surface

    angle_orbit = 2 * np.pi * (frame / total_frames)
    angle_rotation = 2 * np.pi * (frame * earth_rotations / total_frames)

    cx = orbit_radius * np.cos(angle_orbit)
    cy = orbit_radius * np.sin(angle_orbit)
    cz = 0

    dx, dy, dz = Rx_tilt @ np.array([0, 0, 1])
    x1, y1, z1 = cx - (axis_length / 2) * dx, cy - (axis_length / 2) * dy, cz - (axis_length / 2) * dz
    x2, y2, z2 = cx + (axis_length / 2) * dx, cy + (axis_length / 2) * dy, cz + (axis_length / 2) * dz

    earth_axis_line.set_data([x1, x2], [y1, y2])
    earth_axis_line.set_3d_properties([z1, z2])

    earth_pole_line.set_data([x1, x2], [y1, y2])
    earth_pole_line.set_3d_properties([z1, z2])

    if earth_surface:
        earth_surface.remove()

    Rz_rot = np.array([
        [np.cos(angle_rotation), -np.sin(angle_rotation), 0],
        [np.sin(angle_rotation),  np.cos(angle_rotation), 0],
        [0, 0, 1]
    ])
    rotated = Rz_rot @ (Rx_tilt @ np.vstack((x0.flatten(), y0.flatten(), z0.flatten())))
    x_sphere = rotated[0].reshape(x0.shape) + cx
    y_sphere = rotated[1].reshape(y0.shape) + cy
    z_sphere = rotated[2].reshape(z0.shape) + cz

    earth_surface = ax.plot_surface(
        x_sphere, y_sphere, z_sphere,
        color='blue', linewidth=0, zorder=10, alpha=0.4, shade=False
    )

    # Меридианы (вращаются и скрываются по направлению на камеру)
    theta_mer = np.linspace(-np.pi / 2, np.pi / 2, 100)
    camera_dir = np.array([-1, 0, 0])  # Камера смотрит вдоль -X

    for phi, line in meridian_lines:
        x = earth_radius * np.cos(theta_mer) * np.cos(phi)
        y = earth_radius * np.cos(theta_mer) * np.sin(phi)
        z = earth_radius * np.sin(theta_mer)

        coords = np.vstack((x, y, z))
        rotated_coords = Rz_rot @ (Rx_tilt @ coords)

        # Точка в центре меридиана
        center_point = np.mean(rotated_coords, axis=1)
        normal_vec = center_point / np.linalg.norm(center_point)

        dot = np.dot(normal_vec, camera_dir)
        visible = dot > 0

        if visible:
            line.set_data(rotated_coords[0] + cx, rotated_coords[1] + cy)
            line.set_3d_properties(rotated_coords[2] + cz)
        else:
            line.set_data([], [])
            line.set_3d_properties([])

    return [earth_surface, earth_axis_line, earth_pole_line] + [line for _, line in meridian_lines]

# Анимация
ani = FuncAnimation(fig, update, frames=total_frames, interval=50, blit=False)
plt.show()
