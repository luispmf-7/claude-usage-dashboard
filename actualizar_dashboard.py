"""
Automatizacion: Actualizar Claude Usage Dashboard
Ejecuta: viernes 20:00 + dia 19 de cada mes 20:00
- Lee logs reales de .claude/projects/ (JSONL)
- Actualiza Google Sheet con nuevos datos
- Hace push al repo GitHub
"""

import json
import os
import csv
import glob
import subprocess
from datetime import datetime
from pathlib import Path

# ─── CONFIG ──────────────────────────────────────────────────────────────────
CLAUDE_DIR      = Path.home() / ".claude" / "projects"
TOKEN_PATH      = r"C:\Users\luisf\Documents\MiProyecto\token.json"
SHEET_ID        = "1OKTwpv3lRgEaLlzaDTZB-alhVVDW8ULQWMczS_XQFxw"
REPO_DIR        = r"C:\Users\luisf\claude_dashboard_repo"
LOG_FILE        = r"C:\Users\luisf\claude_usage_actualizado.csv"

# Precios API Anthropic (USD por millon de tokens) — fuente: phuryn/claude-usage
PRECIOS = {
    "opus":   {"input": 5.00,  "output": 25.00},
    "sonnet": {"input": 3.00,  "output": 15.00},
    "haiku":  {"input": 1.00,  "output":  5.00},
}
USD_TO_PEN = 3.72

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def get_modelo_key(model_str):
    if not model_str:
        return "sonnet"
    m = model_str.lower()
    if "opus"   in m: return "opus"
    if "haiku"  in m: return "haiku"
    return "sonnet"

def calcular_costo_api(model_str, inp, out):
    k = get_modelo_key(model_str)
    p = PRECIOS[k]
    return (inp / 1_000_000 * p["input"]) + (out / 1_000_000 * p["output"])

def modelo_display(model_str):
    if not model_str: return "Claude Sonnet"
    m = model_str.lower()
    if "opus"  in m: return "Claude Opus"
    if "haiku" in m: return "Claude Haiku"
    return "Claude Sonnet"

# ─── LEER JSONL DE SESIONES ──────────────────────────────────────────────────
def leer_sesiones():
    sesiones = []
    pattern = str(CLAUDE_DIR / "**" / "*.jsonl")
    archivos = glob.glob(pattern, recursive=True)

    print(f"  Archivos JSONL encontrados: {len(archivos)}")

    for archivo in archivos:
        proyecto = Path(archivo).parent.name
        tokens_in = 0
        tokens_out = 0
        modelo = None
        timestamp = None
        turns = 0

        try:
            with open(archivo, "r", encoding="utf-8", errors="ignore") as f:
                for linea in f:
                    try:
                        rec = json.loads(linea.strip())
                        if rec.get("type") == "assistant":
                            uso = rec.get("message", {}).get("usage", {})
                            tokens_in  += uso.get("input_tokens", 0)
                            tokens_out += uso.get("output_tokens", 0)
                            if not modelo:
                                modelo = rec.get("message", {}).get("model", "")
                            ts = rec.get("timestamp", "")
                            if ts and not timestamp:
                                timestamp = ts
                            turns += 1
                    except Exception:
                        continue
        except Exception as e:
            print(f"  Error leyendo {archivo}: {e}")
            continue

        if tokens_in == 0 and tokens_out == 0:
            continue

        # Parsear fecha
        try:
            if timestamp:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                fecha_str = dt.strftime("%Y-%m-%d")
                hora = dt.hour
            else:
                fecha_str = datetime.now().strftime("%Y-%m-%d")
                hora = 10
        except Exception:
            fecha_str = datetime.now().strftime("%Y-%m-%d")
            hora = 10

        # Franja horaria
        if 9 <= hora < 12:
            franja = "Manana"
        elif 15 <= hora < 18:
            franja = "Tarde"
        elif hora >= 20:
            franja = "Noche"
        else:
            franja = "Tarde"

        # Periodo
        try:
            mes = datetime.strptime(fecha_str, "%Y-%m-%d").month
            semana = datetime.strptime(fecha_str, "%Y-%m-%d").isocalendar()[1]
            periodo = f"Semana {semana} ({datetime.strptime(fecha_str, '%Y-%m-%d').strftime('%b')})"
        except Exception:
            periodo = "Semana actual"

        costo_api_usd = calcular_costo_api(modelo, tokens_in, tokens_out)
        costo_api_pen = costo_api_usd * USD_TO_PEN

        sesiones.append({
            "Fecha":         fecha_str,
            "Periodo":       periodo,
            "Proyecto":      proyecto[:30],
            "Modelo":        modelo_display(modelo),
            "Tokens Input":  tokens_in,
            "Tokens Output": tokens_out,
            "Total Tokens":  tokens_in + tokens_out,
            "Costo S/":      round(costo_api_pen, 4),
            "Tipo":          "API" if turns < 5 else "Chat",
            "Duracion min":  max(1, turns * 2),
            "Eficiencia":    round((tokens_in + tokens_out) / max(1, turns * 2), 1),
            "Franja":        franja,
            "Turns":         turns,
            "Costo API USD": round(costo_api_usd, 6),
        })

    sesiones.sort(key=lambda x: x["Fecha"])
    return sesiones

# ─── GUARDAR CSV LOCAL ───────────────────────────────────────────────────────
def guardar_csv(sesiones):
    if not sesiones:
        return
    campos = list(sesiones[0].keys())
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(sesiones)
    print(f"  CSV guardado: {LOG_FILE} ({len(sesiones)} sesiones)")

# ─── ACTUALIZAR GOOGLE SHEET ─────────────────────────────────────────────────
def actualizar_sheet(sesiones):
    try:
        import gspread
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

        with open(TOKEN_PATH) as f:
            t = json.load(f)

        creds = Credentials(
            token=t["token"], refresh_token=t["refresh_token"],
            token_uri=t["token_uri"], client_id=t["client_id"],
            client_secret=t["client_secret"], scopes=t["scopes"]
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SHEET_ID)
        ws = sh.worksheet("Sesiones")

        campos = ["Fecha","Periodo","Proyecto","Modelo","Tokens Input","Tokens Output",
                  "Total Tokens","Costo S/","Tipo","Duracion min","Eficiencia tokens_min","Franja Horaria"]

        rows = [[
            s["Fecha"], s["Periodo"], s["Proyecto"], s["Modelo"],
            s["Tokens Input"], s["Tokens Output"], s["Total Tokens"],
            s["Costo S/"], s["Tipo"], s["Duracion min"], s["Eficiencia"], s["Franja"]
        ] for s in sesiones]

        ws.clear()
        ws.update([campos] + rows)
        print(f"  Google Sheet actualizado: {len(rows)} filas")

    except Exception as e:
        print(f"  WARN Sheet no actualizado: {e}")

# ─── PUSH GITHUB ─────────────────────────────────────────────────────────────
def push_github():
    try:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        os.chdir(REPO_DIR)
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True
        )
        if result.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", f"auto: actualizacion automatica {fecha}"],
                check=True, capture_output=True
            )
            subprocess.run(["git", "push"], check=True, capture_output=True)
            print(f"  GitHub push OK: {fecha}")
        else:
            print("  GitHub: sin cambios nuevos")
    except Exception as e:
        print(f"  WARN GitHub push fallido: {e}")

# ─── MAIN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*50}")
    print(f"  Claude Dashboard — Actualizacion automatica")
    print(f"  {ahora}")
    print(f"{'='*50}")

    print("\n[1/4] Leyendo sesiones JSONL de Claude Code...")
    sesiones = leer_sesiones()
    print(f"  Total sesiones encontradas: {len(sesiones)}")

    if sesiones:
        print("\n[2/4] Guardando CSV local...")
        guardar_csv(sesiones)

        print("\n[3/4] Actualizando Google Sheet...")
        actualizar_sheet(sesiones)

        print("\n[4/4] Push a GitHub...")
        push_github()
    else:
        print("  No se encontraron sesiones con tokens. Verifica ~/.claude/projects/")

    print(f"\n  Fin. Dashboard: https://luispmf-7-claude-usage-dashboard-app-yc6p3i.streamlit.app\n")
