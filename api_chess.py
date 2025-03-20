import requests
import time
import datetime
import math
import calendar
import random
import matplotlib.pyplot as plt
from utils import calculate_win_rate_score, calculate_high_accuracy_score, calculate_weight

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )
}
DEBUG_PASSWORD = "demo123"

def get_account_age_days(username):
    url = f"https://api.chess.com/pub/player/{username}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Error getting profile data:", e)
        return None
    joined = data.get("joined")
    if not joined:
        return None
    current_time = time.time()
    return (current_time - joined) / 86400

def fetch_player_stats(username):
    url = f"https://api.chess.com/pub/player/{username}/stats"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Error getting statistics:", e)
        return {}
    formatos = ["chess_rapid", "chess_bullet", "chess_blitz"]
    stats = {}
    for fmt in formatos:
        if fmt in data:
            last_rating = data[fmt].get("last", {}).get("rating")
            record = data[fmt].get("record", {})
            wins = record.get("win", 0)
            losses = record.get("loss", 0)
            draws = record.get("draw", 0)
            stats[fmt] = {
                "rating": last_rating,
                "wins": wins,
                "losses": losses,
                "draws": draws
            }
    return stats

def fetch_recent_games(username):
    games = []
    now = datetime.datetime.now(datetime.timezone.utc)
    months_to_fetch = []
    if now.day < 15:
        prev_month = (now.replace(day=1) - datetime.timedelta(days=1))
        months_to_fetch.append((prev_month.year, prev_month.month))
    months_to_fetch.append((now.year, now.month))
    for year, month in months_to_fetch:
        url = f"https://api.chess.com/pub/player/{username}/games/{year}/{str(month).zfill(2)}"
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            month_games = data.get("games", [])
        except Exception as e:
            print(f"Error getting games from {year}/{month}: {e}")
            month_games = []
        games.extend(month_games)
    filtered = []
    for game in games:
        if game.get("rules") != "chess":
            continue
        if game.get("time_class") not in ["rapid", "bullet", "blitz"]:
            continue
        if not game.get("rated", False):
            continue
        filtered.append(game)
    return filtered

def fetch_archives(username):
    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        return data.get("archives", [])
    except Exception as e:
        print("Error getting game files:", e)
        return []

def transform_game(game, username):
    username = username.lower()
    if game["white"].get("username", "").lower() == username:
        player_color = "white"
    else:
        player_color = "black"
    player_rating = game[player_color].get("rating")
    raw_result = game[player_color].get("result")
    GAME_RESULTS = {
        "win": "win",
        "agreed": "draw",
        "repetition": "draw",
        "stalemate": "draw",
        "insufficient": "draw",
        "50move": "draw",
        "checkmated": "loss",
        "timeout": "loss",
        "resigned": "loss",
        "lose": "loss",
        "abandoned": "loss"
    }
    result = GAME_RESULTS.get(raw_result, "unknown")
    accuracy = None
    opponent_accuracy = None
    if "accuracies" in game:
        accuracy = game["accuracies"].get(player_color)
        opponent_accuracy = game["accuracies"].get("black" if player_color=="white" else "white")
    timestamp = game.get("end_time")
    return {
        "time_class": game.get("time_class"),
        "player_rating": player_rating,
        "result": result,
        "accuracy": accuracy,
        "opponent_accuracy": opponent_accuracy,
        "timestamp": timestamp
    }

def calculate_format_metrics(fmt, stats_for_fmt, recent_games, username):
    rating = stats_for_fmt.get("rating", 0)
    wins = stats_for_fmt.get("wins", 0)
    losses = stats_for_fmt.get("losses", 0)
    draws = stats_for_fmt.get("draws", 0)
    total = wins + losses + draws
    overall_winrate = (wins / total) if total > 0 else 0
    overall_score = calculate_win_rate_score(overall_winrate, total)
    formato = fmt.replace("chess_", "")
    recents = [game for game in recent_games if game["time_class"] == formato]
    recent_total = len(recents)
    recent_wins = sum(1 for game in recents if game["result"] == "win")
    recent_winrate = (recent_wins / recent_total) if recent_total > 0 else 0
    recent_score = calculate_win_rate_score(recent_winrate, recent_total) if recent_total > 0 else 0
    games_with_accuracy = [game for game in recents if game.get("accuracy") is not None]
    count_accuracy = len(games_with_accuracy)
    if count_accuracy > 0:
        threshold = 80 if rating < 1500 else 90
        high_acc_games = sum(1 for game in games_with_accuracy if game.get("accuracy", 0) >= threshold)
        high_acc_percentage = (high_acc_games / count_accuracy) * 100
    else:
        high_acc_percentage = 0
    accuracy_data = {
        "games_with_accuracy": count_accuracy,
        "high_accuracy_percentage": high_acc_percentage
    }
    accuracy_score = calculate_high_accuracy_score(accuracy_data)
    weighted_sum = 0.35 * overall_score + 0.35 * recent_score + 0.30 * accuracy_score
    details = {
        "rating": rating,
        "overall_winrate": overall_winrate * 100,
        "total_games": total,
        "overall_winrate_score": overall_score,
        "recent_total": recent_total,
        "recent_winrate": recent_winrate * 100,
        "recent_winrate_score": recent_score,
        "accuracy": {
            "games_with_accuracy": count_accuracy,
            "high_accuracy_percentage": high_acc_percentage,
            "accuracy_score": accuracy_score
        },
        "weighted_sum": weighted_sum
    }
    return details

def calculate_risk_score(username):
    account_age_days = get_account_age_days(username)
    stats = fetch_player_stats(username)
    recent_games_raw = fetch_recent_games(username)
    recent_games = []
    for game in recent_games_raw:
        tg = transform_game(game, username)
        if tg["result"] != "unknown":
            recent_games.append(tg)
    account_age_factor = 1.5 if (account_age_days is not None and account_age_days < 60) else 1
    MIN_GAMES = 5
    format_scores = []
    formatos = ["chess_rapid", "chess_bullet", "chess_blitz"]
    for fmt in formatos:
        if fmt in stats:
            metrics = calculate_format_metrics(fmt, stats[fmt], recent_games, username)
            if metrics["recent_total"] < MIN_GAMES:
                continue
            raw_score = metrics["weighted_sum"]
            final_score = min(100, account_age_factor * raw_score)
            format_scores.append((fmt, final_score, metrics))
    if not format_scores:
        return {
            "scores": [],
            "account_age_days": account_age_days,
            "msg": "No hay suficientes partidas en rapid, bullet o blitz."
        }
    format_scores.sort(key=lambda x: x[1], reverse=True)
    return {
        "scores": format_scores,
        "account_age_days": account_age_days,
        "msg": ""
    }

def calculate_weekly_risk_score(week_games, s_global):
    # Calculation of the weekly win rate
    wins = sum(1 for g in week_games if g["result"] == "win")
    total = len(week_games)
    s_weekly = calculate_win_rate_score((wins / total) if total > 0 else 0, total)
    
    # Calculating weekly accuracy
    games_with_accuracy = [g for g in week_games if g.get("accuracy") is not None]
    count_accuracy = len(games_with_accuracy)
    if count_accuracy > 0:
        threshold = 80
        high_acc_games = sum(1 for g in games_with_accuracy if g.get("accuracy", 0) >= threshold)
        high_acc_percentage = (high_acc_games / count_accuracy) * 100
    else:
        high_acc_percentage = 0
    accuracy_score = calculate_high_accuracy_score({
        "games_with_accuracy": count_accuracy,
        "high_accuracy_percentage": high_acc_percentage
    })
    
    # Combination of the three components:
    weighted_sum = 0.35 * s_weekly + 0.35 * s_global + 0.30 * accuracy_score
    final_score = min(100, weighted_sum)
    return final_score

def calculate_risk_score_range(username, start_ts, end_ts):
    """
  Calculates the Risk Score for the range [start_ts, end_ts] using the same logic as the global Risk Score (key 1), but with:
- The total win rate is taken from all games (global),
- The recent win rate and accuracy are calculated only for games
whose timestamp is between start_ts and end_ts.
    """
    #1. Global data: account age and complete statistics
    account_age_days = get_account_age_days(username)
    stats = fetch_player_stats(username)  # Estadísticas totales por formato

    # 2. Download recent games (the same one used by global risk)
    recent_games_raw = fetch_recent_games(username)
   # We transform the games only once
    transformed_games = [transform_game(game, username) for game in recent_games_raw]
    # We filter the games whose timestamp is in the range and with known result
    filtered_games = [tg for tg in transformed_games if tg["timestamp"] and start_ts <= tg["timestamp"] <= end_ts and tg["result"] != "unknown"]

    MIN_GAMES = 5
    format_scores = []
    formatos = ["chess_rapid", "chess_bullet", "chess_blitz"]

    for fmt in formatos:
        if fmt in stats:
            # 3.1 Calculating the total (global) win rate from stats
            s = stats[fmt]
            wins = s.get("wins", 0)
            losses = s.get("losses", 0)
            draws = s.get("draws", 0)
            total_games = wins + losses + draws
            overall_winrate = (wins / total_games) if total_games > 0 else 0
            overall_score = calculate_win_rate_score(overall_winrate, total_games)

            # 3.2 Calculating recent win rate and accuracy, using only range items
            fmt_name = fmt.replace("chess_", "")  # ej. "rapid", "bullet", "blitz"
            recent_games = [game for game in filtered_games if game["time_class"] == fmt_name]
            recent_total = len(recent_games)
            recent_wins = sum(1 for game in recent_games if game["result"] == "win")
            recent_winrate = (recent_wins / recent_total) if recent_total > 0 else 0
            recent_score = calculate_win_rate_score(recent_winrate, recent_total) if recent_total > 0 else 0

            # 3.3 Calculating accuracy with range items only
            rating = s.get("rating", 0)
            games_with_accuracy = [game for game in recent_games if game.get("accuracy") is not None]
            count_accuracy = len(games_with_accuracy)
            if count_accuracy > 0:
                threshold = 80 if rating < 1500 else 90
                high_acc_games = sum(1 for game in games_with_accuracy if game.get("accuracy", 0) >= threshold)
                high_acc_percentage = (high_acc_games / count_accuracy) * 100
            else:
                high_acc_percentage = 0
            accuracy_data = {
                "games_with_accuracy": count_accuracy,
                "high_accuracy_percentage": high_acc_percentage
            }
            accuracy_score = calculate_high_accuracy_score(accuracy_data)

            # 3.4 Weighted combination of the three components:
            # 35% total win rate, 35% recent win rate, and 30% accuracy
            weighted_sum = 0.35 * overall_score + 0.35 * recent_score + 0.30 * accuracy_score

            # If there are fewer than MIN_GAMES games in the range for the format, it is discarded
            if recent_total < MIN_GAMES:
                continue

            # 4. Adjustment for new accounts: Multiply by 1.5 if the account is less than 60 days old
            factor = 1.5 if (account_age_days is not None and account_age_days < 60) else 1
            final_score = min(100, factor * weighted_sum)

            # We save the information for this format
            format_scores.append((fmt, final_score, {
                "overall_winrate": overall_winrate * 100,
                "overall_score": overall_score,
                "recent_total": recent_total,
                "recent_winrate": recent_winrate * 100,
                "recent_score": recent_score,
                "accuracy": {
                    "games_with_accuracy": count_accuracy,
                    "high_accuracy_percentage": high_acc_percentage,
                    "accuracy_score": accuracy_score
                },
                "weighted_sum": weighted_sum
            }))

    if not format_scores:
        return {
            "scores": [],
            "account_age_days": account_age_days,
            "msg": "There are not enough games in the specified range."
        }

    # Ordenamos los formatos de mayor a menor puntuación
    format_scores.sort(key=lambda x: x[1], reverse=True)
    return {
        "scores": format_scores,
        "account_age_days": account_age_days,
        "msg": ""
    }





def analyze_trend_change(username, game_type="global", threshold=8):
    archives = fetch_archives(username)
    if not archives:
        return None, "Could not get game files."
    all_games = []
    for url in archives:
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            games = data.get("games", [])
            if game_type != "global":
                games = [g for g in games if g.get("time_class") == game_type]
            all_games.extend(games)
        except Exception as e:
            print(f"Error getting file {url}: {e}")
    if not all_games:
        return None, "No games were found in the archives."
    games_with_acc = []
    for game in all_games:
        tg = transform_game(game, username)
        if tg.get("accuracy") is not None:
            games_with_acc.append(tg)
    if not games_with_acc:
        return None, "No games with accuracy data were found in the history."
    monthly = {}
    for game in games_with_acc:
        timestamp = game.get("timestamp")
        if timestamp:
            month = datetime.datetime.fromtimestamp(timestamp).strftime("%y-%m")
            if month not in monthly:
                monthly[month] = {"total": 0, "count": 0}
            monthly[month]["total"] += game["accuracy"]
            monthly[month]["count"] += 1
    meses = sorted(monthly.keys())
    avg_accuracy = []
    for mes in meses:
        data = monthly[mes]
        avg = data["total"] / data["count"]
        avg_accuracy.append(avg)
    cambios = []
    for i in range(1, len(avg_accuracy)):
        diff = abs(avg_accuracy[i] - avg_accuracy[i - 1])
        if diff >= threshold:
            cambios.append((meses[i - 1], meses[i], diff))
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.set_title("Change of Trend", color="#D3D3D3")
    ax.plot(meses, avg_accuracy, marker="o", linestyle="-", color="#3F5CB2")
    ax.set_ylabel("Average accuracy", color="white")
    ax.set_xlabel("Mes", color="white")
    ax.tick_params(axis="x", colors="white", labelrotation=90)
    ax.tick_params(axis="y", colors="white")
    ax.grid(True, color="white", alpha=0.3, linestyle="--")
    for prev, curr, diff in cambios:
        idx = meses.index(curr)
        ax.annotate(f"Sudden change: {diff:.1f}",
                    xy=(meses[idx], avg_accuracy[idx]),
                    xytext=(meses[idx], avg_accuracy[idx] + 5),
                    arrowprops=dict(arrowstyle="->", color="red"),
                    color="white")
    fig.tight_layout()
    msg = "Abrupt changes in the trend were detected." if cambios else "No abrupt changes in the trend were detected."
    return fig, msg

def analyze_elo_change(username, game_type="global", threshold=65):
    archives = fetch_archives(username)
    if not archives:
        return None, "No se pudieron obtener archivos de partidas."
    monthly_rating = {}
    for url in archives:
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            games = data.get("games", [])
            if game_type != "global":
                games = [g for g in games if g.get("time_class") == game_type]
            if games:
                games_sorted = sorted(games, key=lambda g: g.get("end_time", 0))
                last_game = games_sorted[-1]
                tg = transform_game(last_game, username)
                if tg.get("player_rating") is not None:
                    month = datetime.datetime.fromtimestamp(last_game.get("end_time")).strftime("%y-%m")
                    monthly_rating[month] = tg.get("player_rating")
        except Exception as e:
            print(f"Error al procesar el archivo {url}: {e}")
    if not monthly_rating:
        return None, "No se pudieron extraer ratings mensuales para el formato seleccionado."
    meses = sorted(monthly_rating.keys())
    ratings = [monthly_rating[mes] for mes in meses]
    cambios = []
    for i in range(1, len(ratings)):
        diff = abs(ratings[i] - ratings[i - 1])
        if diff >= threshold:
            cambios.append((meses[i - 1], meses[i], diff))
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.set_title("Monthly Elo Evolution", color="white")
    ax.plot(meses, ratings, marker="o", linestyle="-", color="#F57C00")
    ax.set_ylabel("Rating Elo", color="white")
    ax.set_xlabel("Mes", color="white")
    ax.tick_params(axis="x", colors="white", labelrotation=90)
    ax.tick_params(axis="y", colors="white")
    ax.grid(True, color="white", alpha=0.3, linestyle="--")
    for prev, curr, diff in cambios:
        idx = meses.index(curr)
        ax.annotate(f"Change: {diff:.0f}",
                    xy=(meses[idx], ratings[idx]),
                    xytext=(meses[idx], ratings[idx] + 50),
                    arrowprops=dict(arrowstyle="->", color="red"),
                    color="white")
    fig.tight_layout()
    msg = "Sudden Elo changes were detected." if cambios else "No sudden Elo changes were detected."
    return fig, msg

def plot_precision_comparison(username, game_type="global"):
    recent_games_raw = fetch_recent_games(username)
    if game_type != "global":
        recent_games_raw = [g for g in recent_games_raw if g.get("time_class") == game_type]
    partidas = []
    for game in recent_games_raw:
        tg = transform_game(game, username)
        if tg.get("accuracy") is not None and tg.get("opponent_accuracy") is not None:
            partidas.append(tg)
    if not partidas:
        return None, "No games with accuracy data were found for the selected type."
    formatos = {}
    for partida in partidas:
        fmt = partida.get("time_class")
        if fmt not in formatos:
            formatos[fmt] = {"usuario": 0, "oponente": 0, "n": 0}
        formatos[fmt]["usuario"] += partida["accuracy"]
        formatos[fmt]["oponente"] += partida["opponent_accuracy"]
        formatos[fmt]["n"] += 1
    categorias = []
    usuario_vals = []
    oponente_vals = []
    for fmt, datos in formatos.items():
        categorias.append(f"{fmt.capitalize()} ({datos['n']})")
        usuario_prom = datos["usuario"] / datos["n"]
        oponente_prom = datos["oponente"] / datos["n"]
        usuario_vals.append(usuario_prom)
        oponente_vals.append(oponente_prom)
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    indices = range(len(categorias))
    ancho = 0.35
    ax.bar([i - ancho/2 for i in indices], usuario_vals, width=ancho, label=username, color="#696969")
    ax.bar([i + ancho/2 for i in indices], oponente_vals, width=ancho, label="Oponente", color="white")
    ax.set_ylabel("Average accuracy", color="white")
    ax.set_title("Accuracy Comparison by Game Type", color="white")
    ax.set_xticks(list(indices))
    ax.set_xticklabels(categorias, color="white")
    ax.tick_params(axis="y", colors="white")
    ax.grid(True, color="white", alpha=0.3, linestyle="--")
    ax.legend(facecolor="black", edgecolor="white", labelcolor="white")
    fig.tight_layout()
    return fig, None

def plot_risk_evolution(username, num_weeks, game_type="global"):
    """
   Generates a graph showing the weekly evolution of the Risk Score over the last num_weeks.
The formula is adjusted to be exactly the same as the normal risk score, i.e.:
- 35% corresponds to the overall win rate (with the new account factor)
- 35% corresponds to the win rate for the week
- 30% corresponds to the accuracy for the week
    """
    now = time.time()
    cutoff = now - num_weeks * 7 * 24 * 3600
    games = []
    # Recent games (limited by cutoff)
    recent_games_raw = fetch_recent_games(username)
    for game in recent_games_raw:
        tg = transform_game(game, username)
        if tg["result"] != "unknown" and tg["timestamp"] and tg["timestamp"] >= cutoff:
            games.append(tg)
    # Add file items to extend the range
    archives = fetch_archives(username)
    for url in archives:
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            archive_games = data.get("games", [])
            for game in archive_games:
                tg = transform_game(game, username)
                if tg["result"] != "unknown" and tg["timestamp"] and tg["timestamp"] >= cutoff:
                    if game_type != "global" and tg["time_class"] != game_type:
                        continue
                    games.append(tg)
        except Exception as e:
            print(f"Error fetching archive {url}: {e}")
    if game_type != "global":
        games = [g for g in games if g.get("time_class") == game_type]
        
    # Calculate s_global identically to the normal risk score:
    stats = fetch_player_stats(username)
    account_age_days = get_account_age_days(username)
    account_age_factor = 1.5 if (account_age_days is not None and account_age_days < 60) else 1
    if game_type == "global":
        total_wins = sum(stats[fmt]["wins"] for fmt in ["chess_rapid", "chess_bullet", "chess_blitz"] if fmt in stats)
        total_losses = sum(stats[fmt]["losses"] for fmt in ["chess_rapid", "chess_bullet", "chess_blitz"] if fmt in stats)
        total_draws = sum(stats[fmt]["draws"] for fmt in ["chess_rapid", "chess_bullet", "chess_blitz"] if fmt in stats)
    else:
        key = f"chess_{game_type}"
        if key in stats:
            total_wins = stats[key]["wins"]
            total_losses = stats[key]["losses"]
            total_draws = stats[key]["draws"]
        else:
            total_wins = total_losses = total_draws = 0
    total_games = total_wins + total_losses + total_draws
    if total_games > 0:
        overall_win_rate = total_wins / total_games
        s_global = calculate_win_rate_score(overall_win_rate, total_games)
    else:
        s_global = 0
  # Apply the new account factor so that it is exactly equal to the normal risk score
    s_global = account_age_factor * s_global

    # Organize the games by week
    weeks = {i: [] for i in range(num_weeks)}
    for game in games:
        timestamp = game.get("timestamp")
        if timestamp:
            diff = now - timestamp
            week_index = int(diff // (7 * 24 * 3600))
            if week_index < num_weeks:
                weeks[week_index].append(game)
    week_labels = []
    risk_scores = []
    for i in range(num_weeks - 1, -1, -1):
        week_games = weeks[i]
        if week_games:
            weekly_risk = calculate_weekly_risk_score(week_games, s_global)
        else:
            weekly_risk = 0
        week_label = f"Semana -{i}" if i > 0 else "Actual"
        week_labels.append(week_label)
        risk_scores.append(weekly_risk)
    if all(score == 0 for score in risk_scores):
        return None, "No games were found in the last specified weeks."
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.plot(week_labels, risk_scores, marker="o", linestyle="-", color="#00FF00")
    ax.set_ylabel("Risk Score", color="white")
    ax.set_title("Evolución Semanal del Risk Score", color="white")
    ax.tick_params(axis="x", colors="white")
    ax.tick_params(axis="y", colors="white")
    ax.grid(True, color="white", alpha=0.3, linestyle="--")
    fig.tight_layout()
    return fig, None
