import os
import sys
import time
import threading
import math
import random
import calendar
import datetime
import requests
import numpy as np
import io
from PIL import ImageDraw
# -------------------------------------------------
# IMPORTS DE TKINTER Y PIL (PARA LOGIN)
# -------------------------------------------------
import tkinter as tk
import customtkinter
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence

# -------------------------------------------------
# IMPORTS DE PYGAME
# -------------------------------------------------
import pygame
from pygame.locals import *
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# =======================================================
# Ajuste para que PyInstaller empaquete todos los recursos
# =======================================================
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

# =======================================================
# Diccionario con las credenciales de usuario
# =======================================================
user_credentials = {
    "admin": "admin",
    
}

# =======================================================
# 1) PANTALLA DE LOGIN
# =======================================================
def show_login():
    """
    Muestra la ventana de login con customtkinter.
    Si se ingresa alguna de las credenciales válidas y se marca 'Remember me',
    se guarda un archivo 'login.txt' en el directorio de trabajo con el formato "username:password".
    Si ya existe, se autocompleta, pero el usuario debe pulsar Login.
    Si el usuario cierra la ventana, se cierra la aplicación.
    """
    # Definir la ruta de login.txt en el directorio de trabajo, que suele ser escribible.
    login_path = os.path.join(os.getcwd(), "login.txt")
    
    background = '#333538'
    total_width = 1150  # 750 (área izquierda) + 400 (área derecha)
    root = customtkinter.CTk()
    root.geometry(f"{total_width}x480")
    root.resizable(False, False)
    root.configure(fg_color=background)
    root.title("Login/Sign up")

    # Si el usuario cierra la ventana, se cierra la app
    def on_closing():
        root.destroy()
        sys.exit()
    root.protocol("WM_DELETE_WINDOW", on_closing)

    customtkinter.set_appearance_mode("Dark")
    customtkinter.set_default_color_theme("blue")

    # Área izquierda para el GIF
    left_canvas_width = int(300 * 2.5)  # 750 píxeles
    left_canvas = tk.Canvas(root, width=left_canvas_width, height=480,
                            highlightthickness=0, bg=background)
    left_canvas.place(x=0, y=0)

    # Cargar el GIF animado (login.gif)
    login_gif_path = os.path.join(base_path, "login.gif")
    try:
        gif = Image.open(login_gif_path)
        frames = [ImageTk.PhotoImage(frame.copy().convert('RGBA'))
                  for frame in ImageSequence.Iterator(gif)]
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar login.gif: {e}")
        root.destroy()
        sys.exit()

    image_item = left_canvas.create_image(0, 0, anchor=tk.NW, image=frames[0])

    def update_frame(ind):
        left_canvas.itemconfig(image_item, image=frames[ind])
        ind = (ind + 1) % len(frames)
        root.after(20, update_frame, ind)

    update_frame(0)

    # Área derecha para widgets
    right_frame_width = total_width - left_canvas_width  # 400 píxeles
    right_frame = tk.Frame(root, bg=background)
    right_frame.place(x=left_canvas_width, y=0,
                      width=right_frame_width, height=480)

    # Logo
    logo_path = os.path.join(base_path, "logo.png")
    try:
        image2 = Image.open(logo_path)
        w, h = image2.size
        image2 = image2.resize((w // 2, h // 2), Image.LANCZOS)
        img2 = ImageTk.PhotoImage(image2)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar logo.png: {e}")
        root.destroy()
        sys.exit()

    label_logo = tk.Label(right_frame, image=img2, bg=background)
    label_logo.image = img2
    label_logo.place(relx=0.5, rely=0.23, anchor='center')

    splash = ['"', 'Fair-Play Analyzer', 'Fair-Play Analyzer', 'Fair-Play Analyzer']
    splashno = random.randrange(1, 4)
    splashs = tk.Label(right_frame, text=splash[splashno],
                       bg=background, fg='green',
                       font=("Helvetica", 12, "italic"))
    splashs.place(relx=0.5, rely=0.36, anchor='center')

    developer = tk.Label(right_frame, text="Developed by Jordi Agost",
                         bg=background, fg='white',
                         font=("Helvetica", 10))
    developer.place(relx=0.5, rely=0.41, anchor='center')

    # Campos de entrada
    user_entry = customtkinter.CTkEntry(master=right_frame,
                                        placeholder_text="Username", width=200)
    user_entry.place(relx=0.5, rely=0.5, anchor='center')

    password_entry = customtkinter.CTkEntry(master=right_frame,
                                            placeholder_text="Password",
                                            width=200, show="*")
    password_entry.place(relx=0.5, rely=0.6, anchor='center')

    remember_var = tk.IntVar()

    def checkbox_event():
        print("checkbox toggled, current value:", remember_var.get())

    checkbox = customtkinter.CTkCheckBox(master=right_frame,
                                         text="Remember username?",
                                         command=checkbox_event,
                                         onvalue=1, offvalue=0)
    checkbox.place(relx=0.5, rely=0.67, anchor='center')

    # Si ya existe login.txt, autocompleta los campos
    if os.path.exists(login_path):
        with open(login_path, "r") as f:
            saved = f.read().strip()
        if ":" in saved:
            saved_user, saved_pass = saved.split(":", 1)
            user_entry.delete(0, tk.END)
            user_entry.insert(0, saved_user)
            password_entry.delete(0, tk.END)
            password_entry.insert(0, saved_pass)
        else:
            user_entry.delete(0, tk.END)
            user_entry.insert(0, saved)
            password_entry.delete(0, tk.END)
            password_entry.insert(0, saved)

    # Botón de login y función actualizada para validar múltiples usuarios
    def attempt_login():
        user_val = user_entry.get()
        pass_val = password_entry.get()
        if user_val in user_credentials and pass_val == user_credentials[user_val]:
            if remember_var.get() == 1:
                with open(login_path, "w") as f:
                    f.write(f"{user_val}:{pass_val}")
            root.destroy()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    button = customtkinter.CTkButton(master=right_frame,
                                     text="Login",
                                     command=attempt_login)
    button.place(relx=0.5, rely=0.75, anchor='center')

    root.mainloop()


# =======================================================
# SI NO HAY ARCHIVO DE LOGIN, SE EJECUTA EL LOGIN
# =======================================================
#show_login()


# =======================================================
# 2) INICIALIZACIÓN DE PYGAME Y TÉRMINOS Y CONDICIONES
# =======================================================
pygame.init()
WIDTH, HEIGHT = int(1300 ), int(760 )
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Análisis Ajedrecístico - Pygame")
clock = pygame.time.Clock()

def wrap_text_simple(text, font_obj, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font_obj.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    return lines

def build_terms_surface(sections, max_width=900):
    line_spacing = 5
    total_height = 0
    rendered = []
    big_title = pygame.font.SysFont("Arial", 32, bold=True)
    main_title_surf = big_title.render("T É R M I N O S   Y   C O N D I C I O N E S", True, (255, 255, 255))
    rendered.append((main_title_surf, 0, total_height))
    total_height += main_title_surf.get_height() + 20
    head_font = pygame.font.SysFont("Arial", 20, bold=True)
    body_font = pygame.font.SysFont("Arial", 16)
    for heading, body in sections:
        heading_surf = head_font.render(heading, True, (255, 255, 255))
        rendered.append((heading_surf, 0, total_height))
        total_height += heading_surf.get_height() + 10
        wrapped = wrap_text_simple(body, body_font, max_width)
        for line in wrapped:
            line_surf = body_font.render(line, True, (128, 128, 128))
            rendered.append((line_surf, 0, total_height))
            total_height += line_surf.get_height() + line_spacing
        total_height += 10
    total_height += 80
    final_surf = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
    final_surf.fill((0, 0, 0, 0))
    for (surf, x, y) in rendered:
        final_surf.blit(surf, (x, y))
    return final_surf, total_height

scroll_sections = [
    ("Terms and Conditions of Use",
     "The use of Risck Score is subject to these terms and conditions. Users are advised to carefully review this document "
     "before proceeding with the installation or use of the software, as their acceptance implies full compliance with the "
     "provisions set forth herein."),
    ("Proper Use",
     "The user agrees to use Fair-Play Analyzer in accordance with principles of integrity, avoiding fraudulent uses or manipulations in games."),
    ("Intellectual Property",
     "All rights over Risk Score, including its algorithmic architecture, software design, user interface, and any other associated component, "
     "are protected under current intellectual property regulations. The reproduction, modification, decompilation, reverse engineering, "
     "redistribution, or any other unauthorized use of the software without the express written consent of its developers is strictly prohibited."),
    ("Limitation of Liability",
     "Risck Score is provided as is, without explicit or implicit guarantees regarding its performance or accuracy. The user acknowledges that the "
     "software may generate false positives or negatives in cheat detection, and no responsibility will be assumed for decisions made based on the "
     "results obtained through the application."),
    ("Data Protection and Privacy",
     "Data collection and processing are carried out in compliance with current regulations. Data will not be shared without consent."),
    ("Applicable Jurisdiction",
     "These terms and conditions are governed by the legislation of France. In case of conflict or dispute arising from their application, the parties agree "
     "to submit to the exclusive jurisdiction of the competent courts of Paris.")
]


def draw_vertical_gradient(surface, top_color, bottom_color):
    h = surface.get_height()
    w = surface.get_width()
    for y in range(h):
        alpha = y / float(h)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * alpha)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * alpha)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * alpha)
        pygame.draw.line(surface, (r, g, b), (0, y), (w, y))

def show_terms_conditions(screen, clock):
    top_color = (0, 180, 0)
    bottom_color = (0, 128, 0)
    max_box_width = 900
    terms_surf, total_height = build_terms_surface(scroll_sections, max_box_width)
    scroll_y = 0
    scroll_speed = 20
    user_input = ""
    prompt_text = "Escriba 'acepto' para continuar: "
    view_width = max_box_width
    view_height = int(HEIGHT * 0.8)
    view_x = (WIDTH - view_width) // 2
    view_y = (HEIGHT - view_height) // 2
    running_tc = True
    while running_tc:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if user_input.strip().lower() == "acepto":
                        running_tc = False
                    else:
                        user_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.key == pygame.K_UP:
                    scroll_y = min(scroll_y + scroll_speed, 0)
                elif event.key == pygame.K_DOWN:
                    max_scroll = -(total_height - view_height)
                    scroll_y = max(scroll_y - scroll_speed, max_scroll)
                else:
                    user_input += event.unicode
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    scroll_y = min(scroll_y + scroll_speed, 0)
                else:
                    max_scroll = -(total_height - view_height)
                    scroll_y = max(scroll_y - scroll_speed, max_scroll)
        draw_vertical_gradient(screen, top_color, bottom_color)
        overlay = pygame.Surface((view_width, view_height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 180), (0, 0, view_width, view_height), border_radius=15)
        screen.blit(overlay, (view_x, view_y))
        area_rect = pygame.Rect(0, -scroll_y, view_width, view_height)
        screen.blit(terms_surf, (view_x, view_y), area_rect)
        small_body = pygame.font.SysFont("Arial", 16)
        prompt_surf = small_body.render(prompt_text + user_input, True, (255, 255, 0))
        screen.blit(prompt_surf, (view_x + 10, view_y + view_height - 30))
        pygame.display.flip()
        clock.tick(30)
    with open("accepted_terms.txt", "w") as f:
        f.write("aceptado")

if not os.path.exists("accepted_terms.txt"):
    show_terms_conditions(screen, clock)


# =======================================================
# 3) IMPORTAMOS MÓDULOS DE ANÁLISIS (api_chess, utils)
# =======================================================
import api_chess
import utils

# =======================================================
# 4) CONFIGURACIÓN DE FUENTES, GIF Y DEMÁS (Pygame)
# =======================================================
font = pygame.font.SysFont("Arial", 20)
title_font = pygame.font.SysFont("Arial", 30, bold=True)

arcade_ttf_path = os.path.join(base_path, "arcade.ttf")
arcade2_ttf_path = os.path.join(base_path, "arcade2.ttf")
arcade3_ttf_path = os.path.join(base_path, "arcade3.ttf")
gif_gif_path = os.path.join(base_path, "gif.gif")

try:
    arcade_font = pygame.font.Font(arcade_ttf_path, 48)
except Exception as e:
    print("No se pudo cargar 'arcade.ttf', se usará fuente por defecto.")
    arcade_font = pygame.font.SysFont("Arial", 48, bold=True)

try:
    arcade_small_font = pygame.font.Font(arcade_ttf_path, 24)
except Exception as e:
    print("No se pudo cargar 'arcade.ttf' para tamaño pequeño, se usará fuente por defecto.")
    arcade_small_font = pygame.font.SysFont("Arial", 24, bold=True)

try:
    arcade2_font = pygame.font.Font(arcade2_ttf_path, 13)
except Exception as e:
    print("No se pudo cargar 'arcade2.ttf', se usará fuente por defecto.")
    arcade2_font = pygame.font.SysFont("Arial", 13, bold=True)

try:
    arcade3_font = pygame.font.Font(arcade3_ttf_path, 12)
except Exception as e:
    print("No se pudo cargar 'arcade3.ttf', se usará fuente por defecto.")
    arcade3_font = pygame.font.SysFont("Arial", 12, bold=True)

def load_gif_frames(filename, scale=0.75):
    frames = []
    try:
        im = Image.open(filename)
        for frame in ImageSequence.Iterator(im):
            frame = frame.convert("RGBA")
            mode = frame.mode
            size = frame.size
            data = frame.tobytes()
            pygame_frame = pygame.image.frombuffer(data, size, mode)
            if scale != 1.0:
                new_width = int(size[0] * scale)
                new_height = int(size[1] * scale)
                pygame_frame = pygame.transform.smoothscale(pygame_frame, (new_width, new_height))
            frames.append(pygame_frame)
    except Exception as e:
        print("Error al cargar el GIF:", e)
    return frames

gif_frames = load_gif_frames(gif_gif_path, scale=0.5)
gif_frame_index = 0
gif_last_update = time.time()
gif_update_delay = 0.1

def draw_gif():
    global gif_frame_index, gif_last_update
    if not gif_frames:
        return
    now = time.time()
    if now - gif_last_update > gif_update_delay:
        gif_frame_index = (gif_frame_index + 1) % len(gif_frames)
        gif_last_update = now
    gif_surface = gif_frames[gif_frame_index]
    gif_rect = gif_surface.get_rect()
    gif_rect.bottom = HEIGHT - 90
    gif_rect.right = WIDTH - 40
    screen.blit(gif_surface, gif_rect)

# =======================================================
# 5) VARIABLES GLOBALES Y ESTADO DE LA APP PYGAME
# =======================================================
active_input = "none"
calendar_start_time = 0

NUM_PARTICLES = 200
particles = []
for _ in range(NUM_PARTICLES):
    pos = [random.uniform(0, WIDTH), random.uniform(0, HEIGHT)]
    vel = [random.randint(-5, 5), random.randint(-5, 5)]
    particles.append({'pos': pos, 'vel': vel})

GREY = (100, 100, 100)
speed_multiplier = 0.2
particle_line_threshold = 75.0
cursor_line_threshold = 100.0

current_screen = 1
screen_titles = {
    1: "Risk Score",
    2: "Comparison",
    3: "Trend",
    4: "Elo Change",
    5: "Range",
    6: "Risk Score Evolution"
}
game_types = ["global", "rapid", "bullet", "blitz"]
selected_game_type = "global"

username = ""
username_input = ""
input_active = True
input_box = pygame.Rect(10, HEIGHT - 40, 500, 30)
arrow_button_rect = pygame.Rect(input_box.right + 10, HEIGHT - 40, 40, 30)
num_mode_button_rect = pygame.Rect(arrow_button_rect.right + 10, HEIGHT - 40, 40, 30)
num_mode_active = False
arrow_pressed = False

analysis_text = ""
analysis_graph_surface = None
analysis_in_progress = False
last_analysis_time = 0
analysis_interval = 5
analysis_start_time = 0
risk_scores_list = []
profile_image_surface = None

risk_period_mode = False
risk_period_state = None
risk_username_input = ""
current_calendar_date = [datetime.datetime.now().year, datetime.datetime.now().month]
start_date = None
end_date = None

risk_evo_username_input = ""
risk_evo_games_input = ""

# =======================================================
# 6) FUNCIONES DE ANIMACIÓN, DIBUJO Y LÓGICA PRINCIPAL
# =======================================================
def draw_chessboard_loading(center, size):
    board_width, board_height = size
    rows, cols = 8, 8
    cell_width = board_width // cols
    cell_height = board_height // rows
    light_color = (240, 217, 181)
    dark_color = (181, 136, 99)
    t = pygame.time.get_ticks() / 1000.0
    board_surface = pygame.Surface((cols * cell_width, rows * cell_height))
    for row in range(rows):
        for col in range(cols):
            base_color = light_color if (row + col) % 2 == 0 else dark_color
            factor = 0.1 * math.sin(3 * t + (row + col))
            r_adj = max(0, min(255, base_color[0] + int(255 * factor)))
            g_adj = max(0, min(255, base_color[1] + int(255 * factor)))
            b_adj = max(0, min(255, base_color[2] + int(255 * factor)))
            cell_color = (r_adj, g_adj, b_adj)
            cell_rect = pygame.Rect(col * cell_width, row * cell_height, cell_width, cell_height)
            pygame.draw.rect(board_surface, cell_color, cell_rect)
    board_rect = board_surface.get_rect(center=center)
    screen.blit(board_surface, board_rect)

def draw_equalizer_global():
    bar_count = 7
    bar_width = 10
    max_height = 50
    gap = 10
    x = WIDTH - 10
    y = HEIGHT - 10
    t = pygame.time.get_ticks() / 1000.0
    colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0),
              (0, 0, 255), (75, 0, 130), (148, 0, 211)]
    for i in range(bar_count):
        phase = i * 0.5
        height = (math.sin(2 * t + phase) + 1) / 2 * max_height
        bar_x = x - (bar_count - i) * (bar_width + gap)
        bar_rect = pygame.Rect(bar_x, y - height, bar_width, height)
        pygame.draw.rect(screen, colors[i % len(colors)], bar_rect)

def figure_to_surface(fig):
    canvas = FigureCanvas(fig)
    canvas.draw()
    size = canvas.get_width_height()
    raw_data = canvas.get_renderer().tostring_argb()
    arr = np.frombuffer(raw_data, dtype=np.uint8).reshape((size[1], size[0], 4))
    rgb_arr = arr[..., 1:4]
    surf = pygame.image.frombuffer(rgb_arr.tobytes(), size, "RGB")
    return surf

def get_risk_label_and_color(score):
    if score <= 35:
        return "Low Risk", (0, 200, 0)
    elif score <= 65:
        return "Medium Risk", (200, 200, 0)
    elif score <= 85:
        return "High Risk", (200, 0, 0)
    else:
        return "Critical Risk", (255, 0, 0)

def draw_circular_progress(surface, center, radius, percentage, color):
    new_radius = int(radius * 1.15)
    thickness = 15
    pygame.draw.circle(surface, (50, 50, 50), center, new_radius, 0)
    pygame.draw.circle(surface, (0, 0, 0), center, new_radius - thickness, 0)
    rect = pygame.Rect(center[0] - new_radius, center[1] - new_radius,
                       new_radius * 2, new_radius * 2)
    end_angle_deg = 360 * (percentage / 100.0)
    start_angle = math.radians(-90)
    end_angle = math.radians(-90 + end_angle_deg)
    pygame.draw.arc(surface, color, rect, start_angle, end_angle, thickness)

def draw_text_with_bg(surface, text, font, text_color, bg_color, pos, padding=5):
    text_surface = font.render(text, True, text_color)
    bg_rect = text_surface.get_rect()
    bg_rect.inflate_ip(padding * 2, padding * 2)
    bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
    bg_surface.fill(bg_color)
    surface.blit(bg_surface, (pos[0] - padding, pos[1] - padding))
    surface.blit(text_surface, pos)

def load_profile_image(username):
    try:
        url = f"https://api.chess.com/pub/player/{username}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        data = response.json()
        avatar_url = data.get("avatar", None)
        if avatar_url:
            img_response = requests.get(avatar_url, headers={"User-Agent": "Mozilla/5.0"}, stream=True)
            img_response.raise_for_status()
            image = Image.open(img_response.raw).convert("RGBA")
            new_size = (int(100 * 1.35), int(100 * 1.35))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            mask = Image.new('L', new_size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + new_size, fill=255)
            output = Image.new("RGBA", new_size)
            output.paste(image, (0, 0), mask)
            mode = output.mode
            size = output.size
            data_bytes = output.tobytes()
            return pygame.image.fromstring(data_bytes, size, mode)
        else:
            return None
    except Exception as e:
        print("The profile picture could not be downloaded:", e)
    return None

def draw_risk_input_bar():
    bar_width, bar_height = 500, 40
    bar_rect = pygame.Rect((WIDTH - bar_width) // 2,
                           (HEIGHT - bar_height) // 2,
                           bar_width, bar_height)
    border_color = (0, 191, 255) if active_input == "risk_period" else (255, 255, 255)
    pygame.draw.rect(screen, (50, 50, 50), bar_rect, border_radius=10)
    pygame.draw.rect(screen, border_color, bar_rect, 2, border_radius=10)
    text = "Investigado: " + risk_username_input
    text_surface = arcade2_font.render(text, True, (255, 255, 255))
    screen.blit(text_surface, (bar_rect.x + 5, bar_rect.y + 5))
    arrow_rect = pygame.Rect(bar_rect.right + 25, bar_rect.y, 40, bar_height)
    pygame.draw.rect(screen, (0, 191, 255), arrow_rect, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), arrow_rect, 2, border_radius=10)
    point1 = (arrow_rect.centerx - 5, arrow_rect.centery - 7)
    point2 = (arrow_rect.centerx - 5, arrow_rect.centery + 7)
    point3 = (arrow_rect.centerx + 7, arrow_rect.centery)
    pygame.draw.polygon(screen, (255, 255, 255), [point1, point2, point3])
    return bar_rect, arrow_rect

def draw_risk_evo_input_bars():
    bar_width, bar_height = 500, 40
    bar_rect1 = pygame.Rect((WIDTH - bar_width) // 2,
                            (HEIGHT - 2 * bar_height - 10) // 2,
                            bar_width, bar_height)
    border_color1 = (0, 191, 255) if active_input == "risk_evo_username" else (255, 255, 255)
    pygame.draw.rect(screen, (50, 50, 50), bar_rect1, border_radius=10)
    pygame.draw.rect(screen, border_color1, bar_rect1, 2, border_radius=10)
    text1 = "Investigado: " + risk_evo_username_input
    text_surface1 = arcade2_font.render(text1, True, (255, 255, 255))
    screen.blit(text_surface1, (bar_rect1.x + 5, bar_rect1.y + 5))
    bar_rect2 = pygame.Rect((WIDTH - bar_width) // 2,
                            bar_rect1.bottom + 10,
                            bar_width, bar_height)
    border_color2 = (0, 191, 255) if active_input == "risk_evo_games" else (255, 255, 255)
    pygame.draw.rect(screen, (50, 50, 50), bar_rect2, border_radius=10)
    pygame.draw.rect(screen, border_color2, bar_rect2, 2, border_radius=10)
    text2 = "Número de semanas: " + risk_evo_games_input
    text_surface2 = arcade2_font.render(text2, True, (255, 255, 255))
    screen.blit(text_surface2, (bar_rect2.x + 5, bar_rect2.y + 5))
    arrow_rect = pygame.Rect(bar_rect1.left - 50, bar_rect1.y, 40, bar_height)
    pygame.draw.rect(screen, (0, 191, 255), arrow_rect, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), arrow_rect, 2, border_radius=10)
    point1 = (arrow_rect.centerx - 5, arrow_rect.centery - 7)
    point2 = (arrow_rect.centerx - 5, arrow_rect.centery + 7)
    point3 = (arrow_rect.centerx + 7, arrow_rect.centery)
    pygame.draw.polygon(screen, (255, 255, 255), [point1, point2, point3])
    return bar_rect1, bar_rect2, arrow_rect

def draw_full_calendar():
    year, month = current_calendar_date
    cal = calendar.monthcalendar(year, month)
    cal_width, cal_height = 800, 400
    calendar_rect = pygame.Rect((WIDTH - cal_width) // 2,
                                (HEIGHT - cal_height) // 2,
                                cal_width, cal_height)
    pygame.draw.rect(screen, (30, 30, 30), calendar_rect)
    try:
        bigger_arcade2 = pygame.font.Font(arcade2_ttf_path, 18)
    except Exception as e:
        bigger_arcade2 = pygame.font.SysFont("Arial", 18, bold=True)
    month_title = f"{calendar.month_name[month]} {year}"
    title_surf = bigger_arcade2.render(month_title, True, (255, 255, 255))
    screen.blit(title_surf, (calendar_rect.x + 10, calendar_rect.y + 10))
    dias = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, dia in enumerate(dias):
        d_surf = font.render(dia, True, (200, 200, 200))
        screen.blit(d_surf, (calendar_rect.x + 50 + i * 100, calendar_rect.y + 50))
    for row_idx, week in enumerate(cal):
        for col_idx, day in enumerate(week):
            cell_rect = pygame.Rect(calendar_rect.x + 50 + col_idx * 100,
                                    calendar_rect.y + 80 + row_idx * 50,
                                    40, 40)
            cell_color = (70, 70, 70)
            if day != 0:
                if start_date and start_date[0] == year and start_date[1] == month and day == start_date[2]:
                    cell_color = (0, 191, 255)
                elif end_date and end_date[0] == year and end_date[1] == month and day == end_date[2]:
                    cell_color = (255, 215, 0)
            pygame.draw.rect(screen, cell_color, cell_rect)
            if day != 0:
                day_surf = arcade2_font.render(str(day), True, (255, 255, 255))
                screen.blit(day_surf, (cell_rect.x + 10, cell_rect.y + 5))
    if start_date is None:
        mode_text = "Select START date"
    elif end_date is None:
        mode_text = "Select END date"
    else:
        mode_text = "Press Enter to confirm range"
    try:
        bigger_arcade3 = pygame.font.Font(arcade3_ttf_path, int(12 * 1.35))
    except Exception as e:
        bigger_arcade3 = pygame.font.SysFont("Arial", int(12 * 1.35), bold=True)
    mode_surf = bigger_arcade3.render(mode_text, True, (255, 255, 255))
    screen.blit(mode_surf, (calendar_rect.x, calendar_rect.y - 40))
    return calendar_rect

def perform_analysis(screen_id, start_ts=None, end_ts=None):
    global analysis_text, analysis_graph_surface, risk_scores_list
    global profile_image_surface, analysis_in_progress, analysis_start_time

    analysis_in_progress = True
    analysis_start_time = time.time()

    if screen_id == 1:
        if start_ts and end_ts:
            result = api_chess.calculate_risk_score_range(username, start_ts, end_ts)
        else:
            result = api_chess.calculate_risk_score(username)
        scores = result["scores"]
        if not scores:
            analysis_text = result["msg"]
            analysis_graph_surface = None
            risk_scores_list = []
        else:
            risk_scores_list = []
            for (fmt, final_score, metrics) in scores:
                label, color = get_risk_label_and_color(final_score)
                risk_scores_list.append({
                    "format": fmt.replace("chess_", ""),
                    "score": final_score,
                    "label": label,
                    "color": color
                })
            analysis_text = ""
            analysis_graph_surface = None
        profile_image_surface = load_profile_image(username)

    elif screen_id == 2:
        fig, err = api_chess.plot_precision_comparison(username, game_type=selected_game_type)
        if fig is not None:
            analysis_graph_surface = figure_to_surface(fig)
            analysis_text = f"{username} vs Oponente"
        else:
            analysis_text = err
            analysis_graph_surface = None

    elif screen_id == 3:
        fig, msg = api_chess.analyze_trend_change(username, game_type=selected_game_type)
        if fig is not None:
            analysis_graph_surface = figure_to_surface(fig)
            analysis_text = msg
        else:
            analysis_text = msg
            analysis_graph_surface = None

    elif screen_id == 4:
        fig, msg = api_chess.analyze_elo_change(username, game_type=selected_game_type)
        if fig is not None:
            analysis_graph_surface = figure_to_surface(fig)
            analysis_text = msg
        else:
            analysis_text = msg
            analysis_graph_surface = None

    elif screen_id == 6:
        try:
            num_weeks = int(risk_evo_games_input)
        except:
            num_weeks = 0
        fig, err = api_chess.plot_risk_evolution(risk_evo_username_input, num_weeks, selected_game_type)
        if fig is not None:
            analysis_graph_surface = figure_to_surface(fig)
            analysis_text = ""
        else:
            analysis_text = err
            analysis_graph_surface = None

    elapsed = time.time() - analysis_start_time
    if elapsed < 2.5:
        time.sleep(2.5 - elapsed)
    analysis_in_progress = False

def start_analysis():
    global last_analysis_time
    current_time = time.time()
    if current_time - last_analysis_time >= analysis_interval and not analysis_in_progress:
        threading.Thread(target=perform_analysis, args=(current_screen,), daemon=True).start()
        last_analysis_time = current_time

def draw_top_bar():
    bar_rect = pygame.Rect(10, 10, WIDTH - 20, 40)
    pygame.draw.rect(screen, (50, 50, 50), bar_rect, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), bar_rect, 2, border_radius=10)
    items_text = "1: Risk Score | 2: Comparison | 3: Trend | 4: Elo Change | 5: Range | 6: Evolution"
    if current_screen != 1:
        items_text += f" | Tipo: {selected_game_type}"
    label_surf = arcade2_font.render(items_text, True, (255, 255, 255))
    text_x = bar_rect.x + 10
    text_y = bar_rect.y + (bar_rect.height - label_surf.get_height()) // 2
    screen.blit(label_surf, (text_x, text_y))

def draw_title():
    t = pygame.time.get_ticks() / 1000.0
    r = int(127 * math.sin(t) + 128)
    g = int(127 * math.sin(t + 2) + 128)
    b = int(127 * math.sin(t + 4) + 128)
    animated_color = (r, g, b)
    title = screen_titles.get(current_screen, "")
    text_surface = arcade_font.render(title, True, animated_color)
    screen.blit(text_surface, (10, 60))

def draw_analysis_result():
    global analysis_text, analysis_graph_surface
    if analysis_in_progress:
        board_center = (WIDTH // 2, HEIGHT // 2)
        board_size = (200, 200)
        draw_chessboard_loading(board_center, board_size)
        return

    if current_screen == 1:
        content_offset_y = int(HEIGHT * 0.25)
        if profile_image_surface:
            profile_y_offset = 80 + content_offset_y
            img_rect = profile_image_surface.get_rect()
            img_rect.midtop = (WIDTH // 2, profile_y_offset)
            screen.blit(profile_image_surface, img_rect)
            circles_y_offset = img_rect.bottom + 60
        else:
            circles_y_offset = HEIGHT // 2

        if len(risk_scores_list) == 0:
            if analysis_text:
                lines = analysis_text.splitlines()
                y_offset = circles_y_offset
                for line in lines:
                    text_surface = font.render(line, True, (255, 255, 255))
                    screen.blit(text_surface, (10, y_offset))
                    y_offset += 25
            return

        circle_spacing = 250
        start_x = WIDTH // 2 - (circle_spacing * (len(risk_scores_list) - 1)) // 2
        center_y = circles_y_offset + 100
        base_radius = 80

        for i, item in enumerate(risk_scores_list):
            fmt = item["format"]
            score = item["score"]
            label = item["label"]
            color = item["color"]
            cx = start_x + i * circle_spacing
            center_pos = (cx, center_y)
            draw_circular_progress(screen, center_pos, base_radius, score, color)
            score_str = f"{int(score)}%"
            tx = center_pos[0] - arcade_small_font.size(score_str)[0] // 2
            ty = center_pos[1] - arcade_small_font.get_height() // 2
            bg_color = (0, 0, 0, 180)
            draw_text_with_bg(screen, score_str, arcade_small_font, (255, 255, 255), bg_color, (tx, ty), padding=4)
            format_text_surface = arcade3_font.render(fmt, True, (255, 255, 255))
            fx = center_pos[0] - format_text_surface.get_width() // 2
            fy = center_pos[1] + int(base_radius * 1.15) + 10
            screen.blit(format_text_surface, (fx, fy))
            risk_text_surface = arcade3_font.render(label, True, color)
            rx = center_pos[0] - risk_text_surface.get_width() // 2
            ry = center_pos[1] + int(base_radius * 1.15) + 35
            screen.blit(risk_text_surface, (rx, ry))
    else:
        if analysis_graph_surface:
            rect = analysis_graph_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(analysis_graph_surface, rect)
        elif analysis_text:
            lines = analysis_text.splitlines()
            y_offset = 100
            for line in lines:
                text_surface = font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (10, y_offset))
                y_offset += 25

def draw_username_input():
    prompt = "User: "
    text = prompt + username_input
    pygame.draw.rect(screen, (50, 50, 50), input_box, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), input_box, 2, border_radius=10)
    text_surface = arcade2_font.render(text, True, (255, 255, 255))
    screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
    arrow_color = (0, 191, 255) if active_input == "normal" else (70, 70, 70)
    pygame.draw.rect(screen, arrow_color, arrow_button_rect, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), arrow_button_rect, 2, border_radius=10)
    point1 = (arrow_button_rect.centerx - 5, arrow_button_rect.centery - 7)
    point2 = (arrow_button_rect.centerx - 5, arrow_button_rect.centery + 7)
    point3 = (arrow_button_rect.centerx + 7, arrow_button_rect.centery)
    pygame.draw.polygon(screen, (255, 255, 255), [point1, point2, point3])
    pygame.draw.rect(screen, (0, 191, 255) if num_mode_active else (70, 70, 70),
                     num_mode_button_rect, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), num_mode_button_rect, 2, border_radius=10)
    mode_text = "123"
    mode_text_surface = arcade2_font.render(mode_text, True, (255, 255, 255))
    text_rect = mode_text_surface.get_rect(center=num_mode_button_rect.center)
    screen.blit(mode_text_surface, text_rect)

def update_and_draw_particles():
    cursor_pos = pygame.mouse.get_pos()
    for particle in particles:
        pos = particle['pos']
        vel = particle['vel']
        pos[0] += vel[0] * clock.get_time() / 1000.0 * 60 * speed_multiplier
        pos[1] += vel[1] * clock.get_time() / 1000.0 * 60 * speed_multiplier
        if pos[0] < 0:
            pos[0] = WIDTH
        elif pos[0] > WIDTH:
            pos[0] = 0
        if pos[1] < 0:
            pos[1] = HEIGHT
        elif pos[1] > HEIGHT:
            pos[1] = 0
    line_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for particle in particles:
        pos = particle['pos']
        for other in particles[particles.index(particle) + 1:]:
            pos2 = other['pos']
            dx = pos2[0] - pos[0]
            dy = pos2[1] - pos[1]
            distance = math.hypot(dx, dy)
            opacity = max(0, 1.0 - (distance / particle_line_threshold))
            if opacity > 0:
                color = (GREY[0], GREY[1], GREY[2], int(opacity * 255))
                pygame.draw.line(line_surface, color, pos, pos2, 1)
    for particle in particles:
        pos = particle['pos']
        dx = cursor_pos[0] - pos[0]
        dy = cursor_pos[1] - pos[1]
        distance = math.hypot(dx, dy)
        opacity = max(0, 1.0 - (distance / cursor_line_threshold))
        if opacity > 0:
            color = (GREY[0], GREY[1], GREY[2], int(opacity * 255))
            pygame.draw.line(line_surface, color, pos, cursor_pos, 1)
    for particle in particles:
        pos_int = (int(particle['pos'][0]), int(particle['pos'][1]))
        pygame.draw.circle(screen, GREY, pos_int, 2)
    screen.blit(line_surface, (0, 0))

arrow_pressed = False

# =======================================================
# 7) BUCLE PRINCIPAL DE LA APLICACIÓN PYGAME
# =======================================================
running = True
while running:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not (risk_period_mode or current_screen == 6):
                if input_box.collidepoint(event.pos):
                    active_input = "normal"
                else:
                    active_input = "none"

            elif risk_period_mode and risk_period_state == "input":
                bar_rect, arrow_rect = draw_risk_input_bar()
                if bar_rect.collidepoint(event.pos):
                    active_input = "risk_period"
                elif arrow_rect.collidepoint(event.pos):
                    pygame.time.wait(500)
                    username = risk_username_input.strip()
                    risk_period_state = "calendar"
                    active_input = "none"
                    calendar_start_time = time.time()

            elif current_screen == 6:
                bar_width, bar_height = 500, 40
                bar_rect1 = pygame.Rect((WIDTH - bar_width) // 2,
                                        (HEIGHT - 2 * bar_height - 10) // 2,
                                        bar_width, bar_height)
                bar_rect2 = pygame.Rect((WIDTH - bar_width) // 2,
                                        bar_rect1.bottom + 10,
                                        bar_width, bar_height)
                arrow_rect = pygame.Rect(bar_rect1.left - 50,
                                         bar_rect1.y,
                                         40, bar_height)
                if bar_rect1.collidepoint(event.pos):
                    active_input = "risk_evo_username"
                elif bar_rect2.collidepoint(event.pos):
                    active_input = "risk_evo_games"
                elif arrow_rect.collidepoint(event.pos):
                    if (risk_evo_username_input.strip() != "" and
                            risk_evo_games_input.strip() != ""):
                        username = risk_evo_username_input.strip()
                        start_analysis()
                else:
                    active_input = "none"

            if risk_period_mode and risk_period_state == "calendar":
                if time.time() - calendar_start_time < 1.0:
                    pass
                else:
                    mx, my = event.pos
                    cal_width, cal_height = 800, 400
                    calendar_area = pygame.Rect((WIDTH - cal_width) // 2,
                                                (HEIGHT - cal_height) // 2,
                                                cal_width, cal_height)
                    if calendar_area.collidepoint(mx, my):
                        year, month = current_calendar_date
                        cal = calendar.monthcalendar(year, month)
                        try:
                            clicked_day = cal[(my - calendar_area.y - 80) // 50][(mx - calendar_area.x - 50) // 100]
                        except IndexError:
                            clicked_day = 0
                        if clicked_day != 0:
                            if start_date is None:
                                start_date = (year, month, clicked_day)
                            elif end_date is None:
                                end_date = (year, month, clicked_day)
                            else:
                                start_date = (year, month, clicked_day)
                                end_date = None

        elif event.type == pygame.MOUSEBUTTONUP:
            if not (risk_period_mode or current_screen == 6):
                if arrow_button_rect.collidepoint(event.pos):
                    arrow_pressed = False
                    if username_input.strip() != "":
                        username = username_input.strip()
                        start_analysis()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                active_input = "none"
                risk_period_mode = False
                risk_period_state = None
                username_input = ""
                risk_username_input = ""
                risk_evo_username_input = ""
                risk_evo_games_input = ""
                current_screen = 1

            elif active_input != "none":
                if active_input == "normal":
                    if event.key == pygame.K_BACKSPACE:
                        username_input = username_input[:-1]
                    else:
                        username_input += event.unicode

                elif active_input == "risk_period":
                    if event.key == pygame.K_BACKSPACE:
                        risk_username_input = risk_username_input[:-1]
                    else:
                        risk_username_input += event.unicode

                elif active_input == "risk_evo_username":
                    if event.key == pygame.K_BACKSPACE:
                        risk_evo_username_input = risk_evo_username_input[:-1]
                    else:
                        risk_evo_username_input += event.unicode

                elif active_input == "risk_evo_games":
                    if event.key == pygame.K_BACKSPACE:
                        risk_evo_games_input = risk_evo_games_input[:-1]
                    else:
                        risk_evo_games_input += event.unicode

            else:
                if risk_period_mode:
                    if risk_period_state == "input":
                        if event.key == pygame.K_RETURN:
                            username = risk_username_input.strip()
                            risk_period_state = "calendar"
                            calendar_start_time = time.time()
                        elif event.key == pygame.K_LEFT:
                            year, month = current_calendar_date
                            if month == 1:
                                current_calendar_date = [year - 1, 12]
                            else:
                                current_calendar_date = [year, month - 1]
                        elif event.key == pygame.K_RIGHT:
                            year, month = current_calendar_date
                            if month == 12:
                                current_calendar_date = [year + 1, 1]
                            else:
                                current_calendar_date = [year, month + 1]
                        elif event.key == pygame.K_RETURN:
                            if start_date and end_date:
                                start_ts = int(datetime.datetime(start_date[0], start_date[1], start_date[2]).timestamp())
                                end_ts = int(datetime.datetime(end_date[0], end_date[1], end_date[2], 23, 59, 59).timestamp())
                                threading.Thread(target=perform_analysis, args=(1, start_ts, end_ts), daemon=True).start()
                                risk_period_mode = False
                                risk_period_state = None
                                start_date = None
                                end_date = None
                    else:
                        if event.key == pygame.K_LEFT:
                            year, month = current_calendar_date
                            if month == 1:
                                current_calendar_date = [year - 1, 12]
                            else:
                                current_calendar_date = [year, month - 1]
                        elif event.key == pygame.K_RIGHT:
                            year, month = current_calendar_date
                            if month == 12:
                                current_calendar_date = [year + 1, 1]
                            else:
                                current_calendar_date = [year, month + 1]
                        elif event.key == pygame.K_RETURN:
                            if start_date and end_date:
                                start_ts = int(datetime.datetime(start_date[0], start_date[1], start_date[2]).timestamp())
                                end_ts = int(datetime.datetime(end_date[0], end_date[1], end_date[2], 23, 59, 59).timestamp())
                                threading.Thread(target=perform_analysis, args=(1, start_ts, end_ts), daemon=True).start()
                                risk_period_mode = False
                                risk_period_state = None
                                start_date = None
                                end_date = None

                elif current_screen == 6:
                    if event.key == pygame.K_LEFT:
                        idx = game_types.index(selected_game_type)
                        selected_game_type = game_types[(idx + len(game_types) - 1) % len(game_types)]
                        analysis_graph_surface = None
                    elif event.key == pygame.K_RIGHT:
                        idx = game_types.index(selected_game_type)
                        selected_game_type = game_types[(idx + 1) % len(game_types)]
                        analysis_graph_surface = None
                    elif event.key == pygame.K_5:
                        risk_period_mode = True
                        risk_period_state = "input"
                        risk_username_input = ""
                        start_date = None
                        end_date = None
                    elif event.key == pygame.K_6:
                        pass
                    elif event.key == pygame.K_1:
                        current_screen = 1
                        analysis_text = ""
                        analysis_graph_surface = None
                        risk_scores_list = []
                    elif event.key == pygame.K_2:
                        current_screen = 2
                        analysis_text = ""
                        analysis_graph_surface = None
                        risk_scores_list = []
                    elif event.key == pygame.K_3:
                        current_screen = 3
                        analysis_text = ""
                        analysis_graph_surface = None
                        risk_scores_list = []
                    elif event.key == pygame.K_4:
                        current_screen = 4
                        analysis_text = ""
                        analysis_graph_surface = None
                        risk_scores_list = []

                else:
                    if event.key == pygame.K_5:
                        risk_period_mode = True
                        risk_period_state = "input"
                        risk_username_input = ""
                        start_date = None
                        end_date = None
                        active_input = "risk_period"
                    elif event.key == pygame.K_6:
                        current_screen = 6
                        risk_evo_username_input = ""
                        risk_evo_games_input = ""
                        active_input = "risk_evo_username"
                        analysis_text = ""
                        analysis_graph_surface = None
                    elif event.key == pygame.K_1:
                        current_screen = 1
                        analysis_text = ""
                        analysis_graph_surface = None
                        risk_scores_list = []
                    elif event.key == pygame.K_2:
                        current_screen = 2
                        analysis_text = ""
                        analysis_graph_surface = None
                        risk_scores_list = []
                    elif event.key == pygame.K_3:
                        current_screen = 3
                        analysis_text = ""
                        analysis_graph_surface = None
                        risk_scores_list = []
                    elif event.key == pygame.K_4:
                        current_screen = 4
                        analysis_text = ""
                        analysis_graph_surface = None
                        risk_scores_list = []
                    elif event.key == pygame.K_LEFT:
                        if current_screen != 1:
                            idx = game_types.index(selected_game_type)
                            selected_game_type = game_types[(idx + len(game_types) - 1) % len(game_types)]
                            analysis_graph_surface = None
                        else:
                            speed_multiplier = max(0, speed_multiplier - 0.1)
                    elif event.key == pygame.K_RIGHT:
                        if current_screen != 1:
                            idx = game_types.index(selected_game_type)
                            selected_game_type = game_types[(idx + 1) % len(game_types)]
                            analysis_graph_surface = None
                        else:
                            speed_multiplier += 0.1

    screen.fill((0, 0, 0))
    update_and_draw_particles()
    draw_top_bar()
    draw_title()

    if risk_period_mode:
        if risk_period_state == "input":
            draw_risk_input_bar()
            draw_username_input()
        elif risk_period_state == "calendar":
            draw_full_calendar()
            draw_username_input()
    elif current_screen == 6:
        if analysis_in_progress:
            draw_analysis_result()
        elif analysis_graph_surface is None:
            draw_risk_evo_input_bars()
        else:
            rect = analysis_graph_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(analysis_graph_surface, rect)
            draw_username_input()
    else:
        draw_analysis_result()
        draw_username_input()

    draw_gif()
    draw_equalizer_global()
    pygame.display.flip()

pygame.quit()
sys.exit()
