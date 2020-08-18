# InterfazOPC

Este programa fue desarrollado como parte del trabajo de fín de máster (TFM) titulado: "Implementación de un controlador predictivo no lineal y una estrategia de optimización en tiempo real" de Daniel Montes, como requísito final para la obtención del título de Máster en Ingeniería Química. Es un puente entre servidores OPC-DA y OPC-UA

## Pre-requisitos:
* Python 3.x versión 32 bits
* OpenOPC (pip install openopc)
* pywintypes (pip install pywin32)
* python-opcua

## Funcionamiento:

InterfazOPC sirve de puente entre servidores OPC-DA (controladores PID, SCADA, simulación de la reacción química) y servidores OPC-UA (controlador predictivo y optimizador en tiempo real). Además, lleva la temporización del control predictivo, es decir, es el componente encargado de realizar periódicamente las llamadas al controlador y al optimizador.

