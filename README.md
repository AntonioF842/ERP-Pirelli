# ERP Pirelli

Un sistema ERP (Enterprise Resource Planning) diseñado para gestionar múltiples áreas dentro de la empresa Pirelli, incluyendo ventas, compras, inventario, recursos humanos, producción, calidad, entre otros.

---

## Tabla de Contenidos

- [¿Qué es ERP Pirelli?](#qué-es-erp-pirelli)
- [Arquitectura del Proyecto](#arquitectura-del-proyecto)
- [Requisitos y Dependencias](#requisitos-y-dependencias)
- [Instalación del Backend](#instalación-del-backend)
- [Instalación del Frontend](#instalación-del-frontend)
- [Ejecución](#ejecución)
- [Notas](#notas)

---

## ¿Qué es ERP Pirelli?

Es una solución completa para gestionar y automatizar los procesos de distintas áreas de la empresa, ofreciendo módulos para ventas, compras, inventario, nómina, control de calidad, proveedores, empleados, etc.

---

## Arquitectura del Proyecto

    erp_pirelli/
    ├── backend/   # API REST en Flask (Python) + SQLAlchemy
    └── frontend/  # Interfaz de escritorio en PyQt6 (Python)

- **Backend:** Provee la API y gestiona la base de datos (MySQL).
- **Frontend:** Aplicación de escritorio creada con PyQt6 para interactuar con el usuario.

---

## Requisitos y Dependencias

### Requerimientos Generales

- Python 3.8 o superior
- Acceso a una base de datos MySQL

### Backend (Flask)

Debes instalar los siguientes paquetes. Puedes hacerlo con pip:

```bash
pip install flask flask_sqlalchemy flask_login flask_cors pymysql
```

### Frontend (PyQt6)

En el frontend, necesitas PyQt6 y posibles librerías auxiliares:

```bash
pip install pyqt6
```

Dependiendo de detalles adicionales, podrías necesitar instalar `requests` o algún paquete para consumir la API REST:

```bash
pip install requests
```

---

## Instalación del Backend

1. Entra al directorio `backend`.
2. Configura en `config.py` los datos de conexión a la base MySQL (usuario, contraseña, base de datos).
   - Por defecto: `'mysql+pymysql://root:Antogarmex1@localhost/erp_pirelli'`
   - Modifica el usuario, contraseña y nombre de base según tu entorno.
3. Inicia el servidor backend:
   ```bash
   python main.py
   ```
   Esto levantará la API en `http://localhost:5000`.

---

## Instalación del Frontend

1. Entra al directorio `frontend`.
2. Ejecuta la aplicación:
   ```bash
   python main.py
   ```
   Esto abrirá la interfaz gráfica del ERP. Por defecto, se conectará a la API en `http://localhost:5000/api`.

---

## Ejecución

1. **Arranca el backend** en una terminal/cmd.
2. **Arranca el frontend** en otra terminal.
3. Debes ver la pantalla de login del sistema.

---
