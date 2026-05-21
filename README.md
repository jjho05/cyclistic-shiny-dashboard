---
title: Cyclistic Shiny Dashboard
emoji: 🚴
colorFrom: blue
colorTo: purple
sdk: docker
app_file: app.py
pinned: false
---

# Cyclistic Bike-Share Shiny Dashboard

Dashboard interactivo de alta fidelidad con tema oscuro diseñado para el análisis del uso del servicio de bicicletas compartidas Cyclistic.

## Características
- Filtros reactivos por tipo de usuario, mes y día de la semana.
- KPIs exactos ponderados de duración y volumen.
- 4 gráficas oscuras personalizadas (Matplotlib/Seaborn).
- Contenedorizado de Docker optimizado para el despliegue automático.

## Ejecución Local
Para probar la aplicación en tu computadora local, ejecuta:
```bash
python3 -m shiny run --reload app.py
```
