<div align="center">

# Ableton MCP · 21 Academy

**Conecta Ableton Live con Claude para automatizar el trabajo repetitivo del estudio.**

La IA organiza, rutea y prepara tu sesión. La música la haces tú.

</div>

---

## ¿Qué es esto?

Una versión ampliada de [AbletonMCP](https://github.com/ahujasid/ableton-mcp) (de Siddharth Ahuja, licencia MIT) mantenida por Franco / 21 Academy. Le agrega lo que un productor necesita para **organizar una sesión** sin hacerlo a mano:

| Herramienta nueva | Qué hace |
|---|---|
| `get_tracks_overview` | Lista todas las pistas con su color, grupo, salida, volumen, paneo, mute y solo, en una sola llamada |
| `set_track_color` | Colorea una pista (hex `#RRGGBB` o nombre: `rojo`, `azul`, `red`, `blue`…) |
| `set_track_output_routing` / `get_track_output_routing` | Cambia o consulta a dónde va el audio de una pista (Main, un bus, Group…) |
| `set_track_volume` | Mueve el fader a un valor en dB (por ejemplo `-6`) |
| `set_track_pan` | Paneo de -1 (izquierda) a 1 (derecha) |
| `set_track_mute` / `set_track_solo` | Mute y solo |
| `configure_tracks` | Aplica nombre, color, salida, volumen, paneo, mute y solo a **muchas pistas en una sola llamada** (más rápido y más barato) |

Todas funcionan en pistas normales, returns y el master (`track_type`: `track`, `return` o `master`).

**Lo que no puede hacer:** agrupar pistas. La API de Ableton no lo permite desde scripts. La solución es trabajar con una plantilla que ya tenga los grupos armados.

**Privacidad:** a diferencia del original, aquí la telemetría viene **apagada por defecto**. No se envía nada a ningún servidor.

---

## Instalación (macOS)

**1. Instala `uv`** (en Terminal):

```bash
brew install uv
```

**2. Instala el Remote Script en Ableton:**

```bash
uvx --from git+https://github.com/francocesti21/ableton-mcp-21 ableton-mcp-install-script
```

Si ya tenías el AbletonMCP original, se reemplaza (el anterior queda respaldado como `__init__.py.bak`).

**3. Agrégalo a Claude:** Claude → Settings → Developer → Edit Config, y dentro de `"mcpServers"`:

```json
"AbletonMCP": {
  "command": "uvx",
  "args": ["--from", "git+https://github.com/francocesti21/ableton-mcp-21", "ableton-mcp"]
}
```

Guarda y cierra Claude por completo (Cmd+Q). Vuelve a abrirlo.

**4. Actívalo en Ableton:** Settings → Link, Tempo & MIDI → Control Surface: **AbletonMCP**, Input y Output en **None**. Si Ableton estaba abierto al instalar, reinícialo.

---

## Ejemplos de pedidos

- *"Muéstrame cómo está organizada la sesión."*
- *"Colorea en rojo todas las pistas de batería y mándalas al grupo DRUMS."*
- *"Pon todas las pistas a -6 dB de partida."*
- *"Mutea las pistas que se llamen COPIA."*

---

## Desarrollo

```bash
uv run --with pytest pytest -q
```

Las pruebas simulan la API de Ableton, así que no hace falta tener Live abierto.

## Créditos y licencia

Basado en [ahujasid/ableton-mcp](https://github.com/ahujasid/ableton-mcp) (MIT). La documentación original está en [README_UPSTREAM.md](README_UPSTREAM.md). Este proyecto mantiene la licencia MIT.
