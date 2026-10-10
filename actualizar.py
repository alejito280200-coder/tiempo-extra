"""Tiempo Extra IA: se ejecuta cada día, trae partidos y noticias, pide a Claude
las ideas y los textos, y guarda todo en docs/data.json."""
import os, json, csv, datetime as dt, urllib.request, xml.etree.ElementTree as ET
import anthropic

FD_TOKEN = os.environ["FOOTBALL_DATA_TOKEN"]
COMPETICIONES = ["CL", "PD", "PL"]  # Champions, LaLiga, Premier (plan gratis de football-data.org)
FEEDS = ["https://feeds.bbci.co.uk/sport/football/rss.xml"]  # agrega aquí feeds RSS en español
MODELO = "claude-sonnet-5-5"

def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "tiempo-extra"})
    return urllib.request.urlopen(req, timeout=30).read()

def partidos():
    hoy = dt.date.today()
    ini, fin = hoy - dt.timedelta(days=2), hoy + dt.timedelta(days=4)
    out = []
    for c in COMPETICIONES:
        url = f"https://api.football-data.org/v4/competitions/{c}/matches?dateFrom={ini}&dateTo={fin}"
        try:
            for m in json.loads(get(url, {"X-Auth-Token": FD_TOKEN}))["matches"]:
                ft = m["score"]["fullTime"]
                out.append({"liga": c, "fecha": m["utcDate"], "estado": m["status"],
                            "local": m["homeTeam"]["shortName"] or m["homeTeam"]["name"],
                            "visita": m["awayTeam"]["shortName"] or m["awayTeam"]["name"],
                            "gl": ft["home"], "gv": ft["away"]})
        except Exception as e:
            print("Error", c, e)
    return out

def noticias():
    out = []
    for f in FEEDS:
        try:
            for it in ET.fromstring(get(f)).iter("item"):
                out.append((it.findtext("title") or "") + ": " + (it.findtext("description") or ""))
                if len(out) >= 20: break
        except Exception as e:
            print("Error feed", f, e)
    return out

def rendimiento():
    # Opcional: rendimiento.csv con columnas tema,alcance (exportado de tus estadísticas de Facebook)
    if not os.path.exists("rendimiento.csv"): return ""
    filas = list(csv.DictReader(open("rendimiento.csv", encoding="utf-8")))
    filas.sort(key=lambda r: -float(r.get("alcance") or 0))
    return "\n".join(f"{r['tema']} -> alcance {r['alcance']}" for r in filas[:15])

def main():
    p, n, r = partidos(), noticias(), rendimiento()
    prompt = f"""Eres el editor de "Tiempo Extra", página de fútbol en Facebook (español neutro, tono dinámico).
Partidos recientes y próximos (JSON): {json.dumps(p, ensure_ascii=False)}
Titulares: {json.dumps(n, ensure_ascii=False)}
Rendimiento pasado de sus publicaciones (si hay): {r or 'sin datos'}
Usa SOLO estos datos; no inventes cifras ni declaraciones. Si algo es rumor, di que NO está confirmado.
Si hay rendimiento pasado, prioriza los temas que más alcance tuvieron.
Devuelve SOLO un JSON: lista de 5 ideas, cada una con las claves:
tipo (Resultado|Previa|Fichaje|Rumor|Análisis), titulo, porque (por qué conviene hoy), descripcion (post de Facebook, 3-5 líneas con emojis),
guion (locución de ~30 s, sin emojis, frases cortas), hashtags (6-8)."""
    msg = anthropic.Anthropic().messages.create(model=MODELO, max_tokens=4000,
                                                messages=[{"role": "user", "content": prompt}])
    txt = msg.content[0].text.strip().removeprefix("```json").removesuffix("```").strip()
    ideas = json.loads(txt)
    os.makedirs("docs", exist_ok=True)
    json.dump({"actualizado": dt.datetime.utcnow().isoformat() + "Z", "partidos": p, "ideas": ideas},
              open("docs/data.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Listo:", len(ideas), "ideas")

if __name__ == "__main__":
    main()
