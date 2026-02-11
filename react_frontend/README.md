# Frontend React - Sistema ISIRT-IA

**Interfaz de usuario moderna** construida con **React 18** y **TypeScript** para el Sistema de Gestión de Incidentes con Asistencia de IA. Esta aplicación de una sola página (SPA) utiliza un stack tecnológico moderno para ofrecer una experiencia de usuario fluida, profesional y mantenible.

## 🎯 Características Principales

### Arquitectura y Framework
- **⚛️ React 18**: Framework moderno con hooks y features concurrentes.
- **📘 TypeScript**: Tipado estático para mayor robustez y mantenibilidad.
- **⚡ Vite**: Build tool de última generación para un desarrollo y compilación ultra rápidos.
- **🧭 React Router**: Navegación declarativa del lado del cliente.
- **🔄 Context API**: Gestión de estado global para la autenticación y datos del usuario.

### UI y Estilos
- **🎨 Tailwind CSS**: Framework CSS utility-first para un diseño rápido y personalizable.
- **📊 Tremor**: Librería de componentes React construida sobre Tailwind, ideal para crear dashboards y UI de datos.
- **📱 Responsive Design**: Interfaz adaptativa para desktop, tablet y móvil.

### Integración con IA
- **🤖 Chatbot Interactivo**: Conversación guiada para el reporte de incidentes con renderizado de Markdown.
- **🎯 Sugerencias Inteligentes**: Clasificación automática de incidentes.
- **🔍 Análisis ISIRT**: Generación de análisis de causa raíz y recomendaciones con IA.

## 🏗️ Arquitectura del Frontend

La arquitectura sigue los principios de **Clean Code** y **Separación de Responsabilidades**.

### Estructura de Carpetas
```
react_frontend/
├── 📁 public/                 # Archivos estáticos (íconos, etc.)
├── 📁 src/
│   ├── 📁 components/        # Componentes React reutilizables (ej. MessageBubble.tsx).
│   │   ├── 📁 admin/
│   │   ├── 📁 incident/
│   │   └── 📁 layout/
│   ├── 📁 context/           # React Context para gestión de estado global (ej. AuthContext).
│   ├── 📁 hooks/             # Hooks personalizados para encapsular lógica (ej. useIncident).
│   ├── 📁 pages/             # Componentes que representan las páginas de la aplicación.
│   ├── 📁 services/          # Módulo centralizado para la comunicación con la API (apiService).
│   ├── 📁 utils/             # Funciones de utilidad puras (ej. textUtils.ts).
│   ├── 📄 App.tsx           # Componente raíz con el enrutador.
│   └── 📄 main.tsx           # Punto de entrada de la aplicación.
├── 📄 package.json           # Dependencias y scripts del proyecto.
├── 📄 tailwind.config.js     # Configuración de Tailwind CSS.
└── 📄 vite.config.ts         # Configuración de Vite.
```

### Flujo de Datos

El flujo de datos es unidireccional, haciendo uso de hooks y contextos para evitar el acoplamiento.

```mermaid
graph TD
    A[Usuario interactúa con la UI] --> B[Componente de Página/UI];
    B --> C[Hook Personalizado (ej. useIncident)];
    C --> D[Servicio API (apiService)];
    D --> E[Backend API];
    E --> D;
    D --> C;
    C --> B;
    B --> A;
```

## 🛠️ Tecnologías y Dependencias Clave

| Tecnología | Propósito |
|---|---|
| React | Framework UI |
| TypeScript | Tipado estático |
| Vite | Build tool y servidor de desarrollo |
| React Router DOM | Enrutamiento del lado del cliente |
| Tailwind CSS | Framework CSS utility-first |
| Tremor | Librería de componentes UI para dashboards |
| marked | Parseo de Markdown a HTML para el chat de IA. |
| DOMPurify | Sanitización de HTML para prevenir ataques XSS. |

## 🚀 Desarrollo

### Prerrequisitos
- **Node.js** 20+
- **npm** 10+
- Backend API ejecutándose.

### Instalación y Ejecución (Local)

Este método es ideal si quieres trabajar únicamente en el frontend.

```bash
# Navegar al directorio del frontend
cd react_frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`.

### Desarrollo con Docker

Si estás utilizando el entorno de Docker Compose del proyecto principal, no necesitas ejecutar los comandos anteriores. Docker se encarga de instalar las dependencias y levantar el servidor. Simplemente modifica los archivos en `react_frontend/src/` y Vite aplicará los cambios en tiempo real (Hot-Reload).

### Scripts Disponibles
```bash
npm run dev          # Inicia el servidor de desarrollo con Hot-Reload.
npm run build        # Compila la aplicación para producción.
npm run lint         # Ejecuta el linter (ESLint) para verificar la calidad del código.
npm run preview      # Sirve el build de producción localmente para previsualización.
```

## 🔒 Seguridad

- **Codificación Segura**: Se utiliza `dangerouslySetInnerHTML` de forma controlada en el componente `MessageBubble` únicamente después de que el contenido Markdown ha sido procesado por `marked` y sanitizado por `DOMPurify` para prevenir ataques XSS.
- **Rutas Protegidas**: Se utiliza `react-router` y un `AuthContext` para proteger las rutas que requieren autenticación.

---
**Estado**: ✅ Migración a React/Tailwind/Tremor completada.
