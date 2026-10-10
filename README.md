# Tiempo Extra IA (autónomo)

Cada día, GitHub ejecuta `actualizar.py`: trae partidos (football-data.org) y titulares (RSS), pide a Claude las ideas y los textos, y publica `docs/data.json`. La página `docs/index.html` los muestra.

## Puesta en marcha (una sola vez)
1. Crea una cuenta en github.com y un repositorio nuevo (público o privado).
2. Sube todo el contenido de esta carpeta (incluida `.github`).
3. Saca una clave gratis en football-data.org (plan gratuito) y una clave de API en console.anthropic.com.
4. En el repositorio: Settings → Secrets and variables → Actions → New secret:
   `FOOTBALL_DATA_TOKEN` y `ANTHROPIC_API_KEY`.
5. Settings → Pages → Source: "Deploy from a branch", rama `main`, carpeta `/docs`. Ahí queda tu enlace.
6. Pestaña Actions → "actualizar" → Run workflow para la primera vez. Luego corre sola cada día (6:00 am Lima).

## Notas
- El uso de la API de Anthropic se cobra por consumo; una corrida diaria de esta app es pequeña.
- Para adaptar las ideas a lo que funciona en tu página, exporta tus publicaciones a `rendimiento.csv` (columnas `tema,alcance`) y súbelo a la raíz.
- Agrega feeds RSS en español en `FEEDS` dentro de `actualizar.py`.
- Los rumores salen marcados como no confirmados; revisa siempre antes de publicar.
