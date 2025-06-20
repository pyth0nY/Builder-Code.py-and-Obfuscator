# Py-Builder Studio 🔥🚀

**La herramienta definitiva con interfaz gráfica para empaquetar, ofuscar y proteger tus aplicaciones Python.**


*(Pega aquí el enlace a una captura de pantalla de tu app cuando la tengas)*

---

## 📝 Índice

-   [¿Qué es Py-Builder Studio?](#-qué-es-py-builder-studio)
-   [✨ Características Principales](#-características-principales)
-   [⚙️ Motores de Ofuscación](#️-motores-de-ofuscación)
    -   [PyArmor (Ofuscación de Bytecode)](#pyarmor-ofuscación-de-bytecode)
    -   [PyFuscator (Ofuscación AST)](#pyfuscator-ofuscación-ast)
-   [💾 Instalación](#-instalación)
-   [▶️ Modo de Uso](#️-modo-de-uso)
-   [🛠️ Tecnologías Utilizadas](#️-tecnologías-utilizadas)
-   [📄 Licencia](#-licencia)

## 🤔 ¿Qué es Py-Builder Studio?

**Py-Builder Studio** nace de la necesidad de simplificar dos procesos complejos en el desarrollo con Python:
1.  **Empaquetado**: Convertir un script `.py` en un ejecutable independiente (`.exe` en Windows) usando el poder de **PyInstaller**.
2.  **Protección**: Asegurar tu código fuente contra la ingeniería inversa y el análisis no autorizado a través de técnicas de **ofuscación avanzadas**.

Esta aplicación combina ambas tareas en una interfaz gráfica **intuitiva y potente**, permitiéndote configurar cada detalle del proceso de construcción sin necesidad de memorizar comandos de terminal.

## ✨ Características Principales

### Empaquetado (PyInstaller)
-   **Interfaz Gráfica Completa**: Olvídate de la línea de comandos.
-   **Configuración Sencilla**:
    -   Selecciona tu script principal (`.py`, `.pyw`).
    -   Elige la carpeta de salida.
    -   Define un nombre personalizado para tu ejecutable.
-   **Opciones de Build Populares**:
    -   `--onefile`: Empaqueta todo en un único archivo ejecutable.
    -   `--noconsole`: Crea una aplicación de ventana sin terminal de fondo.
    -   `--clean`: Limpia los archivos temporales de PyInstaller antes de construir.
-   **Gestión de Assets**:
    -   Añade un **icono personalizado** (`.ico`) a tu aplicación.
    -   Incluye fácilmente **archivos y carpetas adicionales** (imágenes, bases de datos, etc.) que tu app necesite.
-   **Perfiles de Configuración**: **Guarda y carga** tus configuraciones de build en un archivo `.json` para reutilizarlas en el futuro.
-   **Consola de Salida en Vivo**: Monitoriza el progreso del empaquetado en tiempo real directamente en la aplicación.

### Seguridad y Ofuscación
-   **Integración Transparente**: La ofuscación se realiza como un paso previo y automático antes del empaquetado.
-   **Doble Motor de Ofuscación**: Elige entre dos potentes arsenales para proteger tu código.
    -   **PyArmor**: Ofuscación a nivel de bytecode, estándar de la industria.
    -   **PyFuscator**: Nuestro motor personalizado basado en AST, que reescribe tu código fuente con técnicas avanzadas.
-   **Control Total**: Configura cada motor con opciones específicas desde la interfaz.

## ⚙️ Motores de Ofuscación

### PyArmor (Ofuscación de Bytecode)
La opción robusta y probada en batalla. PyArmor no modifica tu código fuente, sino que ofusca el bytecode compilado (`.pyc`), haciendo extremadamente difícil la decompilación.

-   **Nivel de ofuscación de código** (`--obf-code`): Desde ofuscación ligera hasta aplanamiento de bytecode.
-   **Nivel de ofuscación de módulos** (`--obf-mod`): Oculta la estructura de tus imports.
-   **Restricciones de Licencia** (`--restrict`): Embebe una licencia que puede limitar la ejecución del programa a una plataforma específica (Windows/Linux/macOS).

### PyFuscator (Ofuscación AST)
¡Nuestra arma secreta! Este motor analiza tu código fuente como un Árbol de Sintaxis Abstracta (AST) y lo reescribe por completo, aplicando un conjunto de técnicas de ofuscación creativas y muy efectivas.

-   **Ofuscación de Nombres**: Renombra variables, funciones y clases a nombres ilegibles.
-   **Ofuscación de Strings y Números**: Convierte literales de texto y números en expresiones complejas que se resuelven en tiempo de ejecución.
-   **Cifrado de Strings Multi-capa**: Protege tus cadenas de texto más sensibles con un sistema de decodificación en tiempo de ejecución.
-   **Aplanamiento del Flujo de Control (CFF)**: Descompone la lógica de tus funciones en un bucle `while` gigante y una máquina de estados, haciendo el flujo del programa casi imposible de seguir.
-   **Inserción de Código Muerto**: Introduce ramas de código que nunca se ejecutan para confundir a los analizadores.
-   **Predicados Opacos**: Añade condiciones `if` que siempre son verdaderas o falsas pero que parecen complejas, complicando aún más el análisis estático.

## 💾 Instalación

Para poner en marcha Py-Builder Studio, sigue estos sencillos pasos:

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/tu-usuario/py-builder-studio.git
    cd py-builder-studio
    ```

2.  **(Recomendado) Crea un entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    Hemos preparado un archivo `requirements.txt` para ti.
    ```bash
    pip install -r requirements.txt
    ```

¡Y listo! Ya tienes todo lo necesario para empezar.

## ▶️ Modo de Uso

1.  **Ejecuta la aplicación:**
    ```bash
    python BuilderPexe.py
    ```
2.  **Configura el Empaquetador**:
    -   En la pestaña "Empaquetador", selecciona tu script principal y la carpeta de salida.
    -   Ajusta las opciones como "Un solo archivo" o "App de Ventana".
    -   Añade un icono o archivos de datos si es necesario.
3.  **(Opcional) Configura la Seguridad**:
    -   Ve a la pestaña "Seguridad".
    -   Marca la casilla "Habilitar Ofuscación".
    -   Elige tu motor preferido (PyArmor o PyFuscator) y ajusta sus opciones.
4.  **Inicia el Proceso**:
    -   Haz clic en el botón "Iniciar Proceso".
    -   Observa la magia ocurrir en la consola de salida.
5.  **¡Recoge tu .exe!**:
    -   Una vez finalizado, encontrarás tu aplicación ejecutable en la carpeta `dist` dentro de tu directorio de salida.

## 🛠️ Tecnologías Utilizadas

-   **Python 3**: El corazón del proyecto.
-   **PySide6**: Para la creación de la interfaz gráfica de usuario.
-   **qt-material**: Para darle ese increíble tema oscuro y moderno.
-   **PyInstaller**: El motor de empaquetado estándar de la industria.
-   **PyArmor**: El motor de ofuscación de bytecode.
-   **ast & astunparse**: Módulos nativos de Python que impulsan nuestro motor PyFuscator.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---
**Desarrollado con ❤️ para la comunidad Python.**
