import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from shiny import App, render, ui, reactive

# Cargar los datos agrupados optimizados
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, 'cyclistic_aggregated.csv')

if os.path.exists(data_path):
    # Especificar categorías y tipos para rendimiento y ordenamiento por defecto
    week_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    df_all = pd.read_csv(data_path)
    df_all['day_of_week'] = pd.Categorical(df_all['day_of_week'], categories=week_order, ordered=True)
    df_all['tipo_usuario'] = pd.Categorical(df_all['tipo_usuario'], categories=['Miembro Anual', 'Usuario Casual'], ordered=True)
else:
    # Fallback si no existiera
    df_all = pd.DataFrame(columns=['tipo_usuario', 'day_of_week', 'hour', 'rideable_type', 'month_num', 'month_name', 'ride_count', 'avg_duration'])

# --- Configuración Estética de Matplotlib (Estilo Cyber-Dark) ---
def apply_matplotlib_theme():
    plt.style.use('dark_background')
    plt.rcParams.update({
        'figure.facecolor': '#161f30',
        'axes.facecolor': '#161f30',
        'axes.edgecolor': (1.0, 1.0, 1.0, 0.06),
        'axes.grid': True,
        'grid.color': (1.0, 1.0, 1.0, 0.04),
        'grid.linestyle': '--',
        'text.color': '#f3f4f6',
        'axes.labelcolor': '#9ca3af',
        'xtick.color': '#9ca3af',
        'ytick.color': '#9ca3af',
        'font.family': 'sans-serif',
        'figure.autolayout': True,
        'savefig.facecolor': '#161f30'
    })

# Paleta de colores cyber
COLOR_MEMBER = '#00d2ff'  # Azul Neón
COLOR_CASUAL = '#d946ef'  # Morado/Magenta Eléctrico

# --- INTERFAZ DE USUARIO (UI) ---
app_ui = ui.page_fluid(
    # Cargar estilos externos personalizados
    ui.include_css(os.path.join(base_dir, "styles.css")),
    
    ui.row(
        # --- PANEL LATERAL DE CONTROL (FILTROS) ---
        ui.column(
            3,
            ui.div(
                ui.h3("CONFIGURACIÓN", class_="filter-title"),
                
                # Filtro: Tipo de Usuario
                ui.input_checkbox_group(
                    "user_types",
                    "Segmento de Usuario",
                    choices=["Miembro Anual", "Usuario Casual"],
                    selected=["Miembro Anual", "Usuario Casual"]
                ),
                ui.hr(style="border-color: rgba(255,255,255,0.06); margin: 1.5rem 0;"),
                
                # Filtro: Mes del Año
                ui.input_select(
                    "months",
                    "Filtrar por Mes",
                    choices={
                        "Todos": "Todos los Meses",
                        "1": "Enero", "2": "Febrero", "3": "Marzo", "4": "Abril",
                        "5": "Mayo", "6": "Junio", "7": "Julio", "8": "Agosto",
                        "9": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
                    },
                    selected="Todos"
                ),
                ui.hr(style="border-color: rgba(255,255,255,0.06); margin: 1.5rem 0;"),
                
                # Filtro: Día de la Semana
                ui.input_checkbox_group(
                    "days",
                    "Días de Operación",
                    choices=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
                    selected=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                ),
                
                style="margin-top: 1rem;"
            ),
            class_="filter-panel"
        ),
        
        # --- CUERPO PRINCIPAL DEL DASHBOARD ---
        ui.column(
            9,
            # Cabecera de la Aplicación
            ui.div(
                ui.h1("Cyclistic Bike-Share Analysis", class_="dashboard-title"),
                ui.div(
                    "Tablero de Control de Alta Fidelidad para el Análisis de Usuarios Anuales vs. Casuales",
                    class_="dashboard-subtitle"
                ),
                class_="dashboard-header"
            ),
            
            ui.div(
                # --- FILA DE TARJETAS KPI ---
                ui.row(
                    # Tarjeta 1: Total de Viajes
                    ui.column(
                        3,
                        ui.div(
                            ui.div("Viajes Totales", class_="kpi-title"),
                            ui.output_ui("kpi_total_rides"),
                            ui.div("Registros cargados", class_="kpi-footer"),
                            class_="cyber-card"
                        )
                    ),
                    # Tarjeta 2: Miembros Anuales
                    ui.column(
                        3,
                        ui.div(
                            ui.div("Miembros Anuales", class_="kpi-title"),
                            ui.output_ui("kpi_member_percent"),
                            ui.div("Cuota de mercado anual", class_="kpi-footer"),
                            class_="cyber-card"
                        )
                    ),
                    # Tarjeta 3: Usuarios Casuales
                    ui.column(
                        3,
                        ui.div(
                            ui.div("Usuarios Casuales", class_="kpi-title"),
                            ui.output_ui("kpi_casual_percent"),
                            ui.div("Uso recreativo/turístico", class_="kpi-footer"),
                            class_="cyber-card"
                        )
                    ),
                    # Tarjeta 4: Duración Promedio
                    ui.column(
                        3,
                        ui.div(
                            ui.div("Duración Promedio", class_="kpi-title"),
                            ui.output_ui("kpi_avg_duration"),
                            ui.div("Tiempo de viaje (minutos)", class_="kpi-footer"),
                            class_="cyber-card"
                        )
                    ),
                    class_="row-gap-4 mb-4"
                ),
                
                # --- REJILLA DE GRÁFICAS INTERACTIVAS ---
                ui.row(
                    # Gráfica 1: Distribución Horaria
                    ui.column(
                        6,
                        ui.div(
                            ui.div("Uso Horario (Distribución 24 horas)", class_="section-title"),
                            ui.output_plot("plot_hourly_distribution"),
                            class_="cyber-card"
                        )
                    ),
                    # Gráfica 2: Comportamiento por Día de la Semana
                    ui.column(
                        6,
                        ui.div(
                            ui.div("Uso Semanal (Día por Día)", class_="section-title"),
                            ui.output_plot("plot_weekly_distribution"),
                            class_="cyber-card"
                        )
                    ),
                    class_="row-gap-4 mb-4"
                ),
                
                ui.row(
                    # Gráfica 3: Estacionalidad Mensual
                    ui.column(
                        6,
                        ui.div(
                            ui.div("Tendencia Estacional (Viajes Mensuales)", class_="section-title"),
                            ui.output_plot("plot_monthly_trend"),
                            class_="cyber-card"
                        )
                    ),
                    # Gráfica 4: Preferencia de Tipo de Bicicleta
                    ui.column(
                        6,
                        ui.div(
                            ui.div("Preferencias de Bicicleta", class_="section-title"),
                            ui.output_plot("plot_bike_preferences"),
                            class_="cyber-card"
                        )
                    ),
                    class_="row-gap-4 mb-5"
                ),
                style="padding: 0 1.5rem;"
            )
        )
    )
)

# --- LÓGICA DEL SERVIDOR (SERVER) ---
def server(input, output, session):
    
    # 1. Filtro Reactivo de Datos
    @reactive.Calc
    def filtered_data():
        if df_all.empty:
            return df_all
        
        df = df_all.copy()
        
        # Filtro de tipo de usuario
        selected_users = input.user_types()
        if selected_users:
            df = df[df['tipo_usuario'].isin(selected_users)]
        else:
            df = df[df['tipo_usuario'].isin([])]
            
        # Filtro de días de la semana
        selected_days = input.days()
        if selected_days:
            df = df[df['day_of_week'].isin(selected_days)]
        else:
            df = df[df['day_of_week'].isin([])]
            
        # Filtro de meses
        selected_month = input.months()
        if selected_month != "Todos":
            df = df[df['month_num'] == int(selected_month)]
            
        return df

    # --- RENDERIZADO DE KPIs ---
    
    @output
    @render.ui
    def kpi_total_rides():
        df = filtered_data()
        total = int(df['ride_count'].sum()) if not df.empty else 0
        return ui.HTML(f'<span class="kpi-value total">{total:,}</span>')
        
    @output
    @render.ui
    def kpi_member_percent():
        df = filtered_data()
        total = df['ride_count'].sum() if not df.empty else 0
        if total == 0:
            return ui.HTML('<span class="kpi-value member">0.0%</span>')
        
        member_rides = df[df['tipo_usuario'] == 'Miembro Anual']['ride_count'].sum()
        pct = (member_rides / total) * 100
        return ui.HTML(f'<span class="kpi-value member">{pct:.1f}%</span>')
        
    @output
    @render.ui
    def kpi_casual_percent():
        df = filtered_data()
        total = df['ride_count'].sum() if not df.empty else 0
        if total == 0:
            return ui.HTML('<span class="kpi-value casual">0.0%</span>')
            
        casual_rides = df[df['tipo_usuario'] == 'Usuario Casual']['ride_count'].sum()
        pct = (casual_rides / total) * 100
        return ui.HTML(f'<span class="kpi-value casual">{pct:.1f}%</span>')
        
    @output
    @render.ui
    def kpi_avg_duration():
        df = filtered_data()
        total = df['ride_count'].sum() if not df.empty else 0
        if total == 0:
            return ui.HTML('<span class="kpi-value total">0.0</span>')
            
        # Cálculo exacto ponderado de duración promedio
        weighted_duration = (df['avg_duration'] * df['ride_count']).sum() / total
        return ui.HTML(f'<span class="kpi-value total">{weighted_duration:.1f}</span>')

    # --- RENDERIZADO DE GRÁFICAS ---

    # Gráfica 1: Distribución Horaria
    @output
    @render.plot
    def plot_hourly_distribution():
        df = filtered_data()
        apply_matplotlib_theme()
        fig, ax = plt.subplots(figsize=(6, 3.5), dpi=120)
        
        if not df.empty:
            # Agrupar por tipo de usuario y hora
            hourly = df.groupby(['tipo_usuario', 'hour'], observed=False)['ride_count'].sum().reset_index()
            
            for utype, color in [('Miembro Anual', COLOR_MEMBER), ('Usuario Casual', COLOR_CASUAL)]:
                sub_df = hourly[hourly['tipo_usuario'] == utype]
                if not sub_df.empty:
                    # Gráfica de línea suave
                    ax.plot(sub_df['hour'], sub_df['ride_count'], label=utype, color=color, linewidth=2.5, marker='o', markersize=4)
                    ax.fill_between(sub_df['hour'], sub_df['ride_count'], alpha=0.08, color=color)
        
        ax.set_title("Cantidad de Viajes por Hora del Día", fontsize=10, fontweight='bold', pad=10)
        ax.set_xlabel("Hora (24h)", fontsize=8)
        ax.set_ylabel("Viajes Totales", fontsize=8)
        ax.set_xticks(range(0, 24, 2))
        ax.tick_params(axis='both', labelsize=8)
        ax.legend(frameon=False, fontsize=8, loc='upper left')
        
        # Formatear el eje Y con separadores de miles
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        return fig

    # Gráfica 2: Comportamiento por Día de la Semana
    @output
    @render.plot
    def plot_weekly_distribution():
        df = filtered_data()
        apply_matplotlib_theme()
        fig, ax = plt.subplots(figsize=(6, 3.5), dpi=120)
        
        if not df.empty:
            # Agrupar por tipo de usuario y día de la semana
            weekly = df.groupby(['tipo_usuario', 'day_of_week'], observed=False)['ride_count'].sum().reset_index()
            
            # Dibujar barras agrupadas con un espaciador
            days = weekly['day_of_week'].unique()
            x = range(len(days))
            width = 0.35
            
            member_data = weekly[weekly['tipo_usuario'] == 'Miembro Anual']
            casual_data = weekly[weekly['tipo_usuario'] == 'Usuario Casual']
            
            if not member_data.empty:
                ax.bar([pos - width/2 for pos in x], member_data['ride_count'], width, label='Miembro Anual', color=COLOR_MEMBER, edgecolor='none', alpha=0.9)
            if not casual_data.empty:
                ax.bar([pos + width/2 for pos in x], casual_data['ride_count'], width, label='Usuario Casual', color=COLOR_CASUAL, edgecolor='none', alpha=0.9)
                
            ax.set_xticks(x)
            ax.set_xticklabels(days, rotation=15)
            
        ax.set_title("Viajes por Día de la Semana", fontsize=10, fontweight='bold', pad=10)
        ax.set_xlabel("Día de la Semana", fontsize=8)
        ax.set_ylabel("Viajes Totales", fontsize=8)
        ax.tick_params(axis='both', labelsize=8)
        ax.legend(frameon=False, fontsize=8)
        
        # Formatear eje Y
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        return fig

    # Gráfica 3: Estacionalidad Mensual
    @output
    @render.plot
    def plot_monthly_trend():
        df = filtered_data()
        apply_matplotlib_theme()
        fig, ax = plt.subplots(figsize=(6, 3.5), dpi=120)
        
        if not df.empty:
            # Agrupar por tipo de usuario, número y nombre de mes
            monthly = df.groupby(['tipo_usuario', 'month_num', 'month_name'], observed=False)['ride_count'].sum().reset_index()
            monthly.sort_values('month_num', inplace=True)
            
            months_names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
            x = range(1, 13)
            
            for utype, color in [('Miembro Anual', COLOR_MEMBER), ('Usuario Casual', COLOR_CASUAL)]:
                sub_df = monthly[monthly['tipo_usuario'] == utype]
                if not sub_df.empty:
                    # Rellenar meses faltantes si es necesario
                    full_series = pd.DataFrame({'month_num': x})
                    sub_df = pd.merge(full_series, sub_df, on='month_num', how='left').fillna(0)
                    
                    ax.plot(sub_df['month_num'], sub_df['ride_count'], label=utype, color=color, linewidth=2.5, marker='s', markersize=4)
                    ax.fill_between(sub_df['month_num'], sub_df['ride_count'], alpha=0.08, color=color)
            
            ax.set_xticks(x)
            ax.set_xticklabels(months_names)
            
        ax.set_title("Volumen de Viajes Mensuales (Tendencia Anual)", fontsize=10, fontweight='bold', pad=10)
        ax.set_xlabel("Mes", fontsize=8)
        ax.set_ylabel("Viajes Totales", fontsize=8)
        ax.tick_params(axis='both', labelsize=8)
        ax.legend(frameon=False, fontsize=8)
        
        # Formatear eje Y
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        return fig

    # Gráfica 4: Preferencia de Tipo de Bicicleta
    @output
    @render.plot
    def plot_bike_preferences():
        df = filtered_data()
        apply_matplotlib_theme()
        fig, ax = plt.subplots(figsize=(6, 3.5), dpi=120)
        
        if not df.empty:
            # Agrupar por tipo de usuario y tipo de bicicleta
            bikes = df.groupby(['tipo_usuario', 'rideable_type'], observed=False)['ride_count'].sum().reset_index()
            
            # Formatear etiquetas de tipos de bicicletas en español
            bike_mapping = {
                'classic_bike': 'Clásica',
                'electric_bike': 'Eléctrica',
                'docked_bike': 'Acoplada'
            }
            bikes['tipo_bici'] = bikes['rideable_type'].map(bike_mapping)
            
            types = ['Clásica', 'Eléctrica', 'Acoplada']
            x = range(len(types))
            width = 0.35
            
            member_data = bikes[bikes['tipo_usuario'] == 'Miembro Anual']
            casual_data = bikes[bikes['tipo_usuario'] == 'Usuario Casual']
            
            # Rellenar nulos
            m_rides = [member_data[member_data['tipo_bici'] == t]['ride_count'].sum() for t in types]
            c_rides = [casual_data[casual_data['tipo_bici'] == t]['ride_count'].sum() for t in types]
            
            ax.bar([pos - width/2 for pos in x], m_rides, width, label='Miembro Anual', color=COLOR_MEMBER, edgecolor='none', alpha=0.9)
            ax.bar([pos + width/2 for pos in x], c_rides, width, label='Usuario Casual', color=COLOR_CASUAL, edgecolor='none', alpha=0.9)
            
            ax.set_xticks(x)
            ax.set_xticklabels(types)
            
        ax.set_title("Preferencias por Tipo de Bicicleta", fontsize=10, fontweight='bold', pad=10)
        ax.set_xlabel("Tipo de Bicicleta", fontsize=8)
        ax.set_ylabel("Viajes Totales", fontsize=8)
        ax.tick_params(axis='both', labelsize=8)
        ax.legend(frameon=False, fontsize=8)
        
        # Formatear eje Y
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        return fig

# --- INICIALIZACIÓN DE LA APP ---
app = App(app_ui, server)
