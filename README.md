# 🤾🏽 Club Balonmano Barbate — Web Oficial

[![Desplegado en Vercel](https://img.shields.io/badge/Despliegue-Vercel-black?style=flat&logo=vercel)](https://vercel.com)
![Fundado en](https://img.shields.io/badge/Fundaci%C3%B3n-1997-0A2A43?style=flat)
![Localización](https://img.shields.io/badge/Sede-Barbate%2C%20C%C3%A1diz-A8331F?style=flat)

Sitio web oficial del **Club Balonmano Barbate**, referente de balonmano pista y balonmano playa en la Costa de la Luz y Andalucía desde 1997.

---

## 📌 Descripción del Proyecto

El sitio web ofrece una experiencia digital inmersiva y de alto rendimiento que conecta al club con su afición, patrocinadores y cantera. Combina un diseño de inspiración atlántica y marinera con una arquitectura web ligera, accesible y ultra rápida.

- **Pabellón Pista:** Pabellón Municipal de Deportes de Barbate.
- **Sede Playa:** Costa de la Luz / Playa del Carmen (Barbate).
- **Alojamiento & Hosting:** [Vercel](https://vercel.com) (Edge Network Global con despliegue continuo).

---

## 🧭 Estructura del Sitio Web

```text
balonmanobarbate/
├── index.html            # Portada: hero con escudo y brújula, bloque Pista/Playa, el pabellón
├── club.html             # Trayectoria desde 1997, valores del club e instalaciones
├── equipos.html          # Equipos de pista (#pista) y de playa (#playa), por temporada
├── equipaciones.html     # Juegos de pista, portería, playa y ropa de paseo
├── galeria.html          # Galería fotográfica en mosaico, por temporada
├── patrocinadores.html   # Muro de patrocinadores y llamada a colaborar
├── contacto.html         # Datos de contacto, redes y mapa de la sede
├── 404.html              # Página de error con el diseño del sitio
├── assets/
│   ├── css/
│   │   ├── styles.css    # Todo el CSS: tokens de marca, tokens de tema y componentes
│   │   └── fonts.css     # @font-face de las fuentes autoalojadas
│   ├── js/
│   │   ├── main.js       # Menú móvil, botón de tema y pestañas de temporada
│   │   └── theme.js      # Aplica el tema guardado antes de pintar (sin defer)
│   ├── img/              # Fotos en .webp con respaldo .jpg; escudo y logos en .webp
│   │   └── equipaciones/ # Renders de las equipaciones
│   └── fonts/            # Oswald, Source Serif 4 y JetBrains Mono en .woff2 (OFL)
├── vercel.json           # Cabeceras de seguridad y caché inmutable de /assets
├── robots.txt            # Indexación abierta, con referencia al sitemap
├── sitemap.xml           # Las siete páginas indexables
├── README.md             # Documentación general del repositorio
└── CLAUDE.md             # Directrices de arquitectura y estilo para desarrollo asistido por IA
```

> **Arquitectura:** las ocho páginas comparten todo lo de `assets/`. Lo único que sigue
> duplicado en cada archivo es el `<header>` y el `<footer>`, así que un cambio en la
> navegación o en el pie debe replicarse en las ocho. Los detalles están en `CLAUDE.md`.

---

## 🎨 Sistema de Diseño & Tokens

La estética está inspirada en el océano Atlántico, la tradición pesquera y la fuerza del balonmano:

| Token | Hex | Significado / Uso |
| :--- | :--- | :--- |
| `--navy-deep` | `#0A2A43` | Azul noche atlántico (fondos oscuros, cabeceras) |
| `--navy` | `#123A57` | Azul marino corporativo |
| `--gold` | `#D9A73B` | Oro de timón y arena dorada (botones, acentos principales) |
| `--sand` | `#F6F1E4` | Arena clara (fondo principal claro) |
| `--almadraba` | `#A8331F` | Rojo almadraba (llamadas a la acción, detalles enérgicos) |

### 🔤 Tipografías
- **Display / Titulares:** `Oswald` (Sans-Serif de impacto)
- **Cuerpo de Lectura:** `Source Serif 4` (Serif editorial y elegante)
- **Datos y Eyebrows:** `JetBrains Mono` (Monospace de precisión)

---

## 🚀 Despliegue en Vercel

Este proyecto está configurado para desplegarse automáticamente en **Vercel** en cada `push` a la rama principal:

1. **Zero Configuration:** Vercel detecta automáticamente el sitio estático HTML5/CSS3.
2. **Previsualizaciones en ramas (Branch Previews):** Cada Pull Request genera un enlace único de previsualización para revisión visual antes de publicar en producción.
3. **Caché y Assets:** Las imágenes y fuentes se distribuyen a través de la red global Edge de Vercel con tiempos de respuesta ultra bajos.

---

## 💻 Desarrollo Local

No hay build, ni gestor de paquetes, ni dependencias que instalar: basta con servir la carpeta
con cualquier servidor estático. Abrir el HTML con doble clic (`file://`) funciona a medias,
pero no reproduce el comportamiento de las rutas relativas en producción.

```bash
python -m http.server 8000   # http://localhost:8000/index.html
npx serve .                  # alternativa

# O con Live Server en VS Code / Cursor:
# abre index.html y haz clic en "Go Live"
```

Comprobar siempre en los dos tamaños: el menú de navegación cambia a versión móvil en **860 px**.

---

## 📄 Licencia

© Club Balonmano Barbate. Todos los derechos reservados.
