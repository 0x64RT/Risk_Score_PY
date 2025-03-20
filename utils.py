from PIL import Image, ImageDraw
import math

def generate_chessboard_gradient_image(width, height, rows=8, cols=8):
    """
    Devuelve una imagen completamente negra (no se está usando en el main).
    """
    from PIL import Image
    image = Image.new("RGB", (width, height), color=(0, 0, 0))
    return image

def calculate_weight(n):
    return n / (n + 20)

def calculate_win_rate_score(win_rate, total_games):
    weight = calculate_weight(total_games)
    # Escala: a partir de 0.5 de win_rate empieza a sumar
    if win_rate <= 0.5:
        score = 0
    elif win_rate > 0.7:
        score = 100 + ((win_rate - 0.7) / 0.1) * 100
    elif win_rate > 0.6:
        score = 50 + ((win_rate - 0.6) / 0.1) * 50
    elif win_rate > 0.5:
        score = ((win_rate - 0.5) / 0.1) * 50
    else:
        score = 0
    return score * weight

def calculate_high_accuracy_score(accuracy_data):
    n = accuracy_data.get("games_with_accuracy", 0)
    if n == 0:
        return 0
    weight = calculate_weight(n)
    ha = accuracy_data.get("high_accuracy_percentage", 0)
    # Escala: a partir de 10% de partidas con precisión alta empieza a sumar
    if ha <= 10:
        base_score = 0
    elif ha > 30:
        base_score = 100 + (math.floor((ha - 30) / 5)) * 50
    elif ha > 20:
        progress = (ha - 20) / 10
        base_score = 50 + progress * 50
    elif ha > 10:
        progress = (ha - 10) / 10
        base_score = progress * 50
    else:
        base_score = 0
    return base_score * weight
