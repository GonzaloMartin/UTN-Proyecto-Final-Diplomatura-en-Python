# Diplomatura en Python - Proyecto Final
Proyecto Final de la Diplomatura en Python impartida por la Universidad Tecnológica Nacional.

## Autores
- Gonzalo Montalvo | [@GonzaloMartin](https://github.com/GonzaloMartin)
- Matias Falconaro | [@MatiasFalconaro](https://github.com/matiasfalconaro)

## Pautas del Proyecto

### Objetivo
El objetivo de este proyecto es consolidar y aplicar los conocimientos adquiridos durante la Diplomatura.

### Alcance de la Aplicación
El proyecto incluye las siguientes unidades, en las cuales se aplicarán los temas abordados durante el curso:

### Características de la Aplicación

- Toma de datos.
- Uso de funciones, condicionales y bucles.
- Uso de base de datos (SQLite3, a elección).
  - Creación de base de datos y tablas desde Python.
  - Alta de registros en la base de datos, solicitando al usuario ingresar datos a través de un formulario de ventana (con el paquete Tkinter).
- Implementación de regex para la validación de los datos que se ingresan en la app y para el cuadro de búsqueda.
- Realización de ABMC (CRUD) (Alta, Baja, Modificación, Consulta).
- La funcionalidad de interacción con la base de datos y validación de campos se ubican en módulos aparte.
- La app está realizada según el paradigma de POO.
- Se implementó el patrón MVC para el desarrollo.
- Se implementó el patrón Observador para el desarrollo.
- Se implementó el uso de Decoradores.
- Se implementó el uso de conexiones bajo la arquitectura Cliente-Servidor.
- Se adicionaron más controles de excepciones.
- La documentación de toda la app fue hecha en 2 tipos: Documentación funcional y técnica (pdf) y Documentación con Sphinx.


## Ejecución del Proyecto

### Instalacion

Se requiere la versión de `python>=3.9`, en adelante y `pip>=24.0`.

### Dependencias

`pip install -r requirements.txt`

### Ejecutar el Proyecto

`python3 app/main.py`  (Esto iniciará el sistema y levnatará le Servidor).

`python3 app/mvc/t_cliente.py [argumento_opcional]`  (Esto levantará un Cliente).