# 🎯 SENA ADSO · Directorio Estratégico de Aprendices

[![Cloudflare](https://img.shields.io/badge/Deploy-Cloudflare%20Workers%20%26%20Pages-F38020?style=for-the-badge&logo=cloudflare&logoColor=white)](https://workers.cloudflare.com)
[![JavaScript](https://img.shields.io/badge/Architecture-Vanilla%20ES6%2B%20%7C%20Clean%20Code-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org)
[![ISO 25010](https://img.shields.io/badge/Standard-ISO%2FIEC%2025010%20Compliant-blue?style=for-the-badge)](https://iso25000.com)
[![OWASP](https://img.shields.io/badge/Security-OWASP%20Top%2010%20%26%20ISO%2027001-green?style=for-the-badge)](https://owasp.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> **Plataforma estratégica para la gestión y postulación directa a contratos de aprendizaje SENA ADSO** (Análisis y Desarrollo de Software). Diseñada bajo principios de ingeniería de software limpia, alta disponibilidad en el Edge de Cloudflare y seguridad institucional.

---

## 🏛️ Arquitectura del Sistema & Estándares de Ingeniería

El proyecto sigue una arquitectura **JAMstack desacoplada**, con un patrón de **Gestión de Estado Centralizada (Store)** en el cliente y enrutamiento seguro en el Edge con **Cloudflare Workers**.

```
sena-adso-caprendizaje/
├── output/                        # Directorio de Producción / Assets Estáticos
│   ├── index.html                 # Vista Semántica HTML5 (WCAG 2.1 AA / ARIA / SEO)
│   ├── assets/
│   │   ├── css/
│   │   │   └── style.css          # Design Tokens, CSS Variables, Responsive & Motion
│   │   ├── js/
│   │   │   ├── app.js             # Controlador 'use strict', Store, Filtros & Sanitización XSS
│   │   │   └── data.js            # Módulo de datos sincronizado con el registro oficial
│   │   └── data/
│   │       └── empresas.json      # Dataset estructurado JSON
├── worker.js                      # Cloudflare Edge Worker con Cabeceras de Seguridad (CSP, HSTS)
├── wrangler.toml                  # Configuración de despliegue en Cloudflare Workers / Pages
├── package.json                   # Scripts de ciclo de vida (dev, build, deploy)
├── .gitignore                     # Exclusión de artefactos y secretos
├── README.md                      # Documentación técnica
└── LICENSE                        # Licencia MIT
```

---

## 🛡️ Cumplimiento de Normativas y Estándares

### 1. ISO/IEC 25010 (Calidad del Producto de Software)
- **Rendimiento y Eficiencia:** Carga instantánea (< 200ms) sin dependencias pesadas de frameworks, empaquetado directo en el CDN global de Cloudflare.
- **Usabilidad (ISO 9241-210):** Tipografía con jerarquía visual (`Inter` y `JetBrains Mono`), feedback interactivo, soporte para modo oscuro/claro y atajos de teclado (`Escape`).
- **Mantenibilidad:** Separación estricta de responsabilidades (SoC): HTML (Estructura), CSS (Presentación), JS (Lógica de Negocio/Estado).

### 2. ISO/IEC 27001 & OWASP Top 10 (Seguridad de la Información)
- **Prevención de XSS (A03:2021-Injection):** Sanitización contextual estricta (`SecurityUtils.escapeHtml`) en todas las inserciones del DOM.
- **Cabeceras de Seguridad en el Edge (`worker.js`):**
  - `Content-Security-Policy (CSP)` estricta.
  - `Strict-Transport-Security (HSTS)` forzado a 1 año.
  - `X-Content-Type-Options: nosniff` (previene ataques MIME sniffing).
  - `X-Frame-Options: DENY` (anti-Clickjacking).
  - `Referrer-Policy: strict-origin-when-cross-origin`.
  - `Permissions-Policy` bloqueando acceso a hardware sensible.
- **Seguridad en Enlaces:** Atributos `rel="noopener noreferrer"` en todas las redirecciones externas.

---

## 🚀 Características Principales

1. **Protocolo Anti-Bloqueo SGVA:**
   - Permite contactar simultáneamente a decenas de empresas por **Correo Formal**, **WhatsApp** y **LinkedIn**, evitando el bloqueo de 15 días hábiles de la plataforma SGVA.
2. **Generador Automatizado de Outreach Multicanal:**
   - Cartas formales institucionales redactadas profesionalmente con el perfil real del candidato.
   - Enlace directo a la **Hoja de Vida (CV)** en Google Drive.
   - Mensajes directos para WhatsApp y notas de conexión en LinkedIn (< 300 caracteres).
3. **Simulador de Preguntas Técnicas y Filtros ADSO:**
   - Respuestas modelo y tips de portafolio GitHub para cada empresa.
4. **Dock de Comparación Frente a Frente:**
   - Permite seleccionar hasta 3 empresas y evaluar afinidad, calidad web, competencia y salarios proyectados a 5 años.
5. **Exportación Universal:**
   - Descarga el directorio en formatos **Excel (`.xlsx`)** y **CSV (`.csv`)**.

---

## 🛠️ Instalación y Uso Local

### Requisitos Previos:
- [Node.js](https://nodejs.org) (v18+) o navegador web estándar.

### 1. Clonar el Repositorio:
```bash
git clone https://github.com/lakerstrake/sena-adso-caprendizaje.git
cd sena-adso-caprendizaje
```

### 2. Ejecutar Localmente:
Puedes abrir directamente el archivo en tu navegador:
```bash
# Windows
start output/index.html

# Mac
open output/index.html

# Linux
xdg-open output/index.html
```

O usando el servidor local de **Wrangler / Cloudflare**:
```bash
npm install
npm run dev
```

---

## ☁️ Despliegue en Cloudflare

### Opción A: Cloudflare Pages (Recomendado)
```bash
npx wrangler pages deploy output --project-name=sena-caprendizaje-adso
```

### Opción B: Cloudflare Workers
```bash
npm run deploy
```

---

## 👨‍💻 Perfil del Candidato

- **Candidato:** Juan Manuel Lagos Monroy
- **Programa:** Tecnólogo en Análisis y Desarrollo de Software (ADSO) - SENA
- **Contacto:** [jmlagos2003@gmail.com](mailto:jmlagos2003@gmail.com) | (+57) 300 727 9875
- **Portafolio GitHub:** [github.com/lakerstrake](https://github.com/lakerstrake)
- **LinkedIn:** [linkedin.com/in/juan-manuel-lagos-monroy](https://linkedin.com/in/juan-manuel-lagos-monroy)
- **Hoja de Vida Oficial (PDF):** [Google Drive PDF](https://drive.google.com/file/d/1r89tS4JI4OKwSuzyyfPhGn4ylZTRlrln/view?usp=sharing)
- **Certificados Académicos:** [Google Drive Folder](https://drive.google.com/drive/folders/1BZ-qBNdPeYsxW84zIq_ls97UkPlQcHyN?usp=sharing)

---

## 📄 Licencia

Este proyecto está bajo la Licencia [MIT](LICENSE).
