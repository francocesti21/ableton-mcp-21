# Roadmap · MCPs de 21 Academy

Objetivo: que un productor organice su sesión con un pedido, sin tocar el mouse. La IA organiza, rutea y prepara; la música la hace el productor.

**Prioridad: FL Studio** (es donde está la mayoría del público). Ableton como segunda opción.

---

## FL Studio · próxima versión (prioridad 1)

Primer paso: revisar de dónde salió el MCP de FL que Franco tiene instalado (`~/flstudio-mcp`), su licencia y su código, y crear el repositorio propio a partir de él.

Funciones a agregar. Todas existen en la API de scripting de FL (verificado en la documentación de la API):

| Función | API de FL | Para qué |
|---|---|---|
| Asignar cada audio a su canal del mixer | `channels.setTargetFxTrack` (API v1), `mixer.linkChannelToTrack` (API v23) | Lo que en la prueba de CORA BROKE se hizo con 48 clics |
| Renombrar canales del Channel Rack | `channels.setChannelName` (API v1) | Que el Channel Rack tenga los mismos nombres que el mixer |
| Renombrar, colorear y mutear pistas de la playlist | `playlist.setTrackName`, `playlist.setTrackColor`, `playlist.muteTrack` | Playlist ordenada visualmente por grupo |
| Una herramienta en lote ("organizar sesión") | Combina las anteriores | Toda la sesión en 2 o 3 llamadas, menos consumo |

Lo que la API de FL **no** permite (se resuelve con plantilla base o a mano):
- Crear canales en el mixer.
- Anclar canales a la derecha (solo existe `getTrackDockSide`, para leer).
- Mover clips o reordenar pistas en la playlist.
- Exportar stems, guardar el proyecto, cargar plugins.

## Ableton · próxima versión (prioridad 2)

Hecho en v1.8.x: vista general de la sesión, colores, ruteo, volumen en dB, paneo, mute, solo y configuración en lote. Probado en Ableton Live 12 el 20 de noviembre de 2026.

Pendiente:
- Borrar pistas y returns (`song.delete_track`, `song.delete_return_track`) para poder limpiar la sesión antes de importar.
- Importar stems desde una carpeta a pistas nuevas dentro de cada grupo (crear la pista en una posición dentro del grupo; hay que comprobar que quede agrupada).
- Agrupar pistas: la API de Ableton no lo permite (`group_track` es de solo lectura). Se trabaja con una plantilla que ya tenga los grupos.

## Común a los dos

- **Configuración inicial del productor** (la primera vez que se usa): pico de partida para el gain staging (default -6 dB), formato de entrega (default WAV 24 bit, 44.1 kHz). Configuración de Franco: -3 dB, WAV 24 bit, 48 kHz.
- **Detección de copias** en los stems recibidos (Master, Current, export completo, demos): muteadas y agrupadas aparte.
- **Detección de duplicados RAW / procesado** en voces (por ejemplo ADLIBS FX y ADLIBS RAW): avisar, no decidir.
- **Tempo desde el audio** del master para ajustar el proyecto.
- Regla de diseño: solo trabajo repetitivo con respuesta correcta. Nada de componer, elegir sonidos ni decidir la mezcla.
