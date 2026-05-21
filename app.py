import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from shiny import App, render, ui, reactive
from dotenv import load_dotenv

# Cargar configuraciones de proveedores e inteligencia
import providers
import logic

# Cargar variables de entorno del archivo .env local
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, '.env'))

# Cargar los datos agrupados optimizados
data_path = os.path.join(base_dir, 'cyclistic_aggregated.csv')

if os.path.exists(data_path):
    week_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    df_all = pd.read_csv(data_path)
    df_all['day_of_week'] = pd.Categorical(df_all['day_of_week'], categories=week_order, ordered=True)
    df_all['tipo_usuario'] = pd.Categorical(df_all['tipo_usuario'], categories=['Miembro Anual', 'Usuario Casual'], ordered=True)
else:
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

# Paleta de colores de segmentos
COLOR_MEMBER = '#00d2ff'  # Azul Neón
COLOR_CASUAL = '#d946ef'  # Morado/Magenta Eléctrico

# --- INTERFAZ DE USUARIO (UI) ---
app_ui = ui.page_sidebar(
    # PANEL LATERAL DE CONTROL (FILTROS PREMIUM SEPHORA-STYLE PERO SOBRIO)
    ui.sidebar(
        # Badge de la Suite Olvera
        ui.div(
            "OLVERA AI SYSTEM",
            class_="sidebar-title-badge"
        ),
        
        # Caja explicativa de grado forense
        ui.div(
            ui.div(
                "📊 AUDITORÍA REACTIVA",
                class_="sidebar-description-title"
            ),
            ui.div(
                "Este sistema realiza minería analítica sobre millones de registros históricos de Cyclistic. "
                "Filtre el corpus de viajes y active a Olvera AI para obtener resúmenes estratégicos.",
                class_="sidebar-description-text"
            ),
            class_="sidebar-description-box"
        ),
        
        # Cabecera de los filtros
        ui.div("🚨 CONTROL DE FILTROS", class_="sidebar-filter-header"),
        
        # Filtro: Tipo de Usuario
        ui.input_checkbox_group(
            "user_types",
            "Segmento de Usuario:",
            choices=["Miembro Anual", "Usuario Casual"],
            selected=["Miembro Anual", "Usuario Casual"]
        ),
        ui.hr(style="border-color: rgba(255,255,255,0.06); margin: 1.5rem 0;"),
        
        # Filtro: Mes del Año
        ui.input_select(
            "months",
            "Filtrar por Mes:",
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
            "Días de Operación:",
            choices=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
            selected=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        ),
        width=290
    ),
    
    # CUERPO PRINCIPAL DEL TABLERO
    ui.div(
        # Cargar estilos externos personalizados
        ui.include_css(os.path.join(base_dir, "styles.css")),
        
        # Línea de estilo neo-stripe minimalista (Monocromática sobria)
        ui.div(class_="neon-top-stripe"),
        
        # Cabecera superior
        ui.div(
            ui.h1("Cyclistic Bike-Share Analysis", class_="dashboard-title"),
            ui.div(
                "Auditoría Estratégica de Movilidad & Copiloto Inteligente de Negocios",
                class_="dashboard-subtitle"
            ),
            class_="dashboard-header"
        ),
        
        # Estructura de Pestañas (Dashboard vs Olvera AI)
        ui.navset_tab(
            # PESTAÑA 1: DASHBOARD
            ui.nav_panel(
                "📊 Dashboard de Viajes",
                ui.div(
                    # --- FILA DE TARJETAS KPI ---
                    ui.row(
                        # Tarjeta 1: Total de Viajes
                        ui.column(
                            3,
                            ui.div(
                                ui.div("Viajes Totales", class_="kpi-title"),
                                ui.output_ui("kpi_total_rides"),
                                ui.div("Registros agrupados", class_="kpi-footer"),
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
                    
                    # --- REJILLA DE GRÁFICAS CON EXPLICACIONES EJECUTIVAS ---
                    ui.row(
                        # Gráfica 1: Distribución Horaria
                        ui.column(
                            6,
                            ui.div(
                                ui.div("Uso Horario (Distribución 24 horas)", class_="cyber-card-header"),
                                ui.output_plot("plot_hourly_distribution"),
                                ui.div(
                                    ui.div("ANÁLISIS DE COMPORTAMIENTO DIARIO", class_="explanation-title"),
                                    ui.div(
                                        "Los miembros muestran picos definidos en horas de entrada y salida laboral (08:00 y 17:00), confirmando un uso utilitario. Los casuales tienen un incremento constante y suave hacia la tarde, indicando un uso recreativo.",
                                        class_="explanation-text"
                                    ),
                                    class_="explanation-box"
                                ),
                                class_="cyber-card"
                            )
                        ),
                        # Gráfica 2: Comportamiento por Día de la Semana
                        ui.column(
                            6,
                            ui.div(
                                ui.div("Uso Semanal (Día por Día)", class_="cyber-card-header"),
                                ui.output_plot("plot_weekly_distribution"),
                                ui.div(
                                    ui.div("COMPORTAMIENTO SEMANAL", class_="explanation-title"),
                                    ui.div(
                                        "El volumen de miembros se mantiene estable de lunes a viernes y baja ligeramente en fines de semana. Por el contrario, los usuarios casuales se disparan dramáticamente el sábado y domingo, consolidando su perfil recreativo.",
                                        class_="explanation-text"
                                    ),
                                    class_="explanation-box"
                                ),
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
                                ui.div("Tendencia Estacional (Viajes Mensuales)", class_="cyber-card-header"),
                                ui.output_plot("plot_monthly_trend"),
                                ui.div(
                                    ui.div("ESTACIONALIDAD ANUAL", class_="explanation-title"),
                                    ui.div(
                                        "Ambos segmentos exhiben una fuerte contracción en los meses de invierno (diciembre a febrero) debido a las temperaturas extremas. El pico de actividad ocurre en verano (junio a agosto), donde la demanda se triplica.",
                                        class_="explanation-text"
                                    ),
                                    class_="explanation-box"
                                ),
                                class_="cyber-card"
                            )
                        ),
                        # Gráfica 4: Preferencia de Tipo de Bicicleta
                        ui.column(
                            6,
                            ui.div(
                                ui.div("Preferencias de Bicicleta", class_="cyber-card-header"),
                                ui.output_plot("plot_bike_preferences"),
                                ui.div(
                                    ui.div("PREFERENCIA DE EQUIPOS", class_="explanation-title"),
                                    ui.div(
                                        "Las bicicletas clásicas y eléctricas son altamente demandadas por ambos segmentos. Cabe destacar que las bicicletas acopladas ('docked') son utilizadas de manera exclusiva por los usuarios casuales.",
                                        class_="explanation-text"
                                    ),
                                    class_="explanation-box"
                                ),
                                class_="cyber-card"
                            )
                        ),
                        class_="row-gap-4 mb-5"
                    )
                )
            ),
            
            # PESTAÑA 2: OLVERA AI
            ui.nav_panel(
                "💬 Copilot Olvera AI",
                ui.div(
                    # Banner de Bienvenida Olvera AI
                    ui.div(
                        ui.output_ui("welcome_ui"),
                        style="margin-bottom: 1.5rem;"
                    ),
                    # Componente Shiny Chat
                    ui.chat_ui("chat"),
                    # Barra de herramientas de estado inferior
                    ui.output_ui("chat_toolbar_ui"),
                    style="padding: 1.5rem; max-width: 900px; margin: 0 auto;"
                )
            ),
            
            # PESTAÑA 3: REPORTE EJECUTIVO
            ui.nav_panel(
                "📖 Reporte Ejecutivo",
                ui.div(
                    # Grid Layout para el Reporte Ejecutivo
                    ui.row(
                        # Columna Izquierda: Introducción, Preguntas y Procesamiento
                        ui.column(
                            6,
                            # Sección 1: Tarea Empresarial y Contexto
                            ui.div(
                                ui.div("1. Contexto & Tarea Empresarial", class_="report-card-header"),
                                ui.div(
                                    ui.HTML("""
                                        <p>El objetivo central de este proyecto es <strong>maximizar la rentabilidad de Cyclistic</strong>. Dado que los analistas financieros determinaron que los miembros anuales son significativamente más rentables que los ciclistas ocasionales, la dirección estratégica ha definido que la <strong>conversión de usuarios ocasionales a socios anuales</strong> es la vía más sólida para el crecimiento corporativo duradero.</p>
                                        <div class="report-badge-container">
                                            <span class="report-badge-sober">FOCO ESTRATÉGICO</span>
                                            <span class="report-badge-sober">CONVERSIÓN DE SEGMENTO</span>
                                        </div>
                                    """),
                                    class_="report-card-body"
                                ),
                                class_="report-card"
                            ),
                            
                            # Sección 2: La Problemática y Preguntas Clave
                            ui.div(
                                ui.div("2. Problemática y Preguntas Orientadoras", class_="report-card-header"),
                                ui.div(
                                    ui.HTML("""
                                        <div class="quote-block-sober">
                                            ¿En qué se diferencian los socios anuales y los ciclistas ocasionales con respecto al uso de las bicicletas de Cyclistic?
                                        </div>
                                        <p style="margin-top: 1rem;">Esta pregunta clave busca aislar los comportamientos de ambos tipos de usuarios para diseñar estrategias de marketing altamente personalizadas, con el fin de incentivar a los ciclistas ocasionales a adquirir membresías anuales.</p>
                                        <h4 class="report-sub-title">Interesados Clave (Stakeholders):</h4>
                                        <ul class="report-bullet-list">
                                            <li><strong>Lily Moreno:</strong> Directora de marketing y responsable del desarrollo de campañas para promover el programa de bicicletas compartidas.</li>
                                            <li><strong>Equipo de análisis de datos de marketing:</strong> Responsable de recopilar, analizar y reportar los datos estratégicos de los viajes.</li>
                                            <li><strong>Equipo ejecutivo de Cyclistic:</strong> Decisores finales sumamente detallistas que evaluarán y aprobarán el plan recomendado.</li>
                                        </ul>
                                    """),
                                    class_="report-card-body"
                                ),
                                class_="report-card"
                            ),
                            
                            # Sección 3: Preparación y Procesamiento de Datos
                            ui.div(
                                ui.div("3. Preparación y Procesamiento de Datos", class_="report-card-header"),
                                ui.div(
                                    ui.HTML("""
                                        <p>Se utilizaron los datos históricos reales de viajes de la empresa (red de Chicago, Divvy Trip Data) de 12 meses consecutivos (abril 2021 a marzo 2022).</p>
                                        <div class="alert-block-sober">
                                            <strong>Integridad de los Datos (Evaluación ROCCC):</strong> Confiables, Originales, Integrales (5,723,532 viajes brutos), Actuales y Citados bajo licencia de uso abierto de Chicago.
                                        </div>
                                        <p style="margin-top: 1rem;"><strong>Privacidad de Datos (PII):</strong> Por estrictas directivas de privacidad, se eliminó y prohibió el uso de cualquier información de identificación personal (nombres, tarjetas, direcciones), impidiendo conectar viajes con individuos específicos.</p>
                                        <p><strong>Herramientas Utilizadas:</strong> Python 3.11 y la librería Pandas (debido a que Excel colapsa ante los 5.7M de registros). Se removieron 4,797 registros erróneos (viajes <= 0 min o > 24 horas), logrando un conjunto limpio con un <strong>99.92% de integridad</strong>.</p>
                                    """),
                                    class_="report-card-body"
                                ),
                                class_="report-card"
                            ),
                            class_="row-gap-4"
                        ),
                        
                        # Columna Derecha: Hallazgos, Estrategias de Marketing y Conclusión
                        ui.column(
                            6,
                            # Sección 4: Qué se Encontró (Hallazgos Críticos)
                            ui.div(
                                ui.div("4. Qué se Encontró (Hallazgos Críticos)", class_="report-card-header"),
                                ui.div(
                                    ui.HTML("""
                                        <p>El análisis descriptivo revela un comportamiento radicalmente distinto entre ambos perfiles de usuarios. Los socios anuales utilizan el servicio de forma utilitaria y predecible, mientras que los casuales muestran un perfil marcadamente recreativo.</p>
                                        <div class="metrics-grid-sober">
                                            <div class="metric-item-sober">
                                                <div class="metric-val-sober" style="color:var(--color-member);">55.5%</div>
                                                <div class="metric-lbl-sober">Viajes por Socios</div>
                                            </div>
                                            <div class="metric-item-sober">
                                                <div class="metric-val-sober" style="color:var(--color-casual);">44.5%</div>
                                                <div class="metric-lbl-sober">Viajes por Casuales</div>
                                            </div>
                                            <div class="metric-item-sober">
                                                <div class="metric-val-sober">13.1 min</div>
                                                <div class="metric-lbl-sober">Duración Media Socio</div>
                                            </div>
                                            <div class="metric-item-sober">
                                                <div class="metric-val-sober">26.5 min</div>
                                                <div class="metric-lbl-sober">Duración Media Casual</div>
                                            </div>
                                        </div>
                                        <ul class="report-bullet-list" style="margin-top: 1rem;">
                                            <li><strong>Frecuencia y Días:</strong> Los socios tienen una demanda estable de lunes a viernes (commuting). Los casuales se concentran masivamente los fines de semana (picos los sábados con >500k viajes).</li>
                                            <li><strong>Curva Horaria:</strong> Los socios muestran dos picos sumamente definidos en días laborables (08:00 AM y 05:00 PM). Los casuales muestran una curva suave y creciente que alcanza su máximo por la tarde (03:00 PM - 05:00 PM).</li>
                                            <li><strong>Tipos de Bicicleta:</strong> Ambos prefieren las bicicletas clásicas y eléctricas. Sin embargo, las <strong>Bicicletas Acopladas (Docked Bikes)</strong> son utilizadas única y exclusivamente por los usuarios ocasionales.</li>
                                        </ul>
                                    """),
                                    class_="report-card-body"
                                ),
                                class_="report-card"
                            ),
                            
                            # Sección 5: Estrategias de Marketing Recomendadas
                            ui.div(
                                ui.div("5. Estrategias de Marketing de Conversión", class_="report-card-header"),
                                ui.div(
                                    ui.HTML("""
                                        <div class="strat-item-sober">
                                            <div class="strat-num-sober">1</div>
                                            <div class="strat-text-sober">
                                                <strong>Campaña en Estaciones Turísticas & Fines de Semana:</strong>
                                                Activar campañas digitales y códigos QR de conversión georreferenciados los sábados y domingos de verano en puntos turísticos de alta afluencia (parques, playas y centros recreativos), ofreciendo un descuento instantáneo al adquirir la membresía.
                                            </div>
                                        </div>
                                        <div class="strat-item-sober">
                                            <div class="strat-num-sober">2</div>
                                            <div class="strat-text-sober">
                                                <strong>Membresías Intermedias (Fin de Semana o Estacionales):</strong>
                                                Crear un 'Pase de Verano' o una 'Membresía Anual de Fines de Semana' (acceso exclusivo vie-dom) a una fracción del costo. Esto reduce la barrera psicológica inicial y actúa como un puente natural hacia la membresía anual completa.
                                            </div>
                                        </div>
                                        <div class="strat-item-sober">
                                            <div class="strat-num-sober">3</div>
                                            <div class="strat-text-sober">
                                                <strong>Concientización Basada en Ahorro Acumulado:</strong>
                                                Utilizar la aplicación móvil y notificaciones por correo electrónico después de viajes casuales prolongados (>20 minutos), mostrando un comparativo financiero: <em>'Hoy gastaste $X. Con la membresía anual, este viaje te habría costado $0 y habrías ahorrado $Y este mes'</em>.
                                            </div>
                                        </div>
                                    """),
                                    class_="report-card-body"
                                ),
                                class_="report-card"
                            ),
                            
                            # Sección 6: Conclusión
                            ui.div(
                                ui.div("6. Conclusión y Recomendación Ejecutiva", class_="report-card-header"),
                                ui.div(
                                    ui.HTML("""
                                        <p>La conversión de usuarios ocasionales a socios anuales no es solo una meta de marketing, sino la estrategia financiera de mayor rentabilidad y menor costo de adquisición para Cyclistic. La riqueza de los datos confirma que <strong>los ciclistas casuales ya aman y usan intensamente el sistema</strong>; la clave está en romper la barrera de compromiso financiero anual mediante productos flexibles, ofertas contextuales en tiempo real y la visualización directa del ahorro económico personal.</p>
                                        <div class="signature-sober">
                                            <div class="signature-line-sober"></div>
                                            <div class="signature-title-sober">Presentado al Consejo Ejecutivo de Cyclistic</div>
                                            <div class="signature-subtitle-sober">Por el Equipo de Análisis Computacional de Datos de Marketing</div>
                                        </div>
                                    """),
                                    class_="report-card-body"
                                ),
                                class_="report-card"
                            ),
                            class_="row-gap-4"
                        ),
                        class_="row-gap-4 mb-5"
                    ),
                    style="padding: 1.5rem; max-width: 1200px; margin: 0 auto;"
                )
            ),
            id="main_nav_tabs"
        )
    ),
    title="Cyclistic Performance Suite"
)

# --- LÓGICA DEL SERVIDOR (SERVER) ---
def server(input, output, session):
    
    # Estado reactivo para limpiar banner de bienvenida al enviar un mensaje
    is_empty = reactive.Value(True)
    
    # Inicialización del componente Chat
    chat = ui.Chat(id="chat")
    
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
            
        weighted_duration = (df['avg_duration'] * df['ride_count']).sum() / total
        return ui.HTML(f'<span class="kpi-value total">{weighted_duration:.1f}</span>')

    # --- RENDERIZADO DE GRÁFICAS ---

    # Gráfica 1: Distribución Horaria
    @output
    @render.plot
    def plot_hourly_distribution():
        df = filtered_data()
        apply_matplotlib_theme()
        fig, ax = plt.subplots(figsize=(6, 3.2), dpi=120)
        
        if not df.empty:
            hourly = df.groupby(['tipo_usuario', 'hour'], observed=False)['ride_count'].sum().reset_index()
            
            for utype, color in [('Miembro Anual', COLOR_MEMBER), ('Usuario Casual', COLOR_CASUAL)]:
                sub_df = hourly[hourly['tipo_usuario'] == utype]
                if not sub_df.empty:
                    ax.plot(sub_df['hour'], sub_df['ride_count'], label=utype, color=color, linewidth=2.5, marker='o', markersize=3.5)
                    ax.fill_between(sub_df['hour'], sub_df['ride_count'], alpha=0.08, color=color)
        
        ax.set_title("Cantidad de Viajes por Hora del Día", fontsize=9, fontweight='bold', pad=8)
        ax.set_xlabel("Hora (24h)", fontsize=7.5)
        ax.set_ylabel("Viajes Totales", fontsize=7.5)
        ax.set_xticks(range(0, 24, 2))
        ax.tick_params(axis='both', labelsize=7.5)
        ax.legend(frameon=False, fontsize=7.5, loc='upper left')
        
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        return fig

    # Gráfica 2: Comportamiento por Día de la Semana
    @output
    @render.plot
    def plot_weekly_distribution():
        df = filtered_data()
        apply_matplotlib_theme()
        fig, ax = plt.subplots(figsize=(6, 3.2), dpi=120)
        
        if not df.empty:
            weekly = df.groupby(['tipo_usuario', 'day_of_week'], observed=False)['ride_count'].sum().reset_index()
            
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
            ax.set_xticklabels(days, rotation=10)
            
        ax.set_title("Viajes por Día de la Semana", fontsize=9, fontweight='bold', pad=8)
        ax.set_xlabel("Día de la Semana", fontsize=7.5)
        ax.set_ylabel("Viajes Totales", fontsize=7.5)
        ax.tick_params(axis='both', labelsize=7.5)
        ax.legend(frameon=False, fontsize=7.5)
        
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        return fig

    # Gráfica 3: Estacionalidad Mensual
    @output
    @render.plot
    def plot_monthly_trend():
        df = filtered_data()
        apply_matplotlib_theme()
        fig, ax = plt.subplots(figsize=(6, 3.2), dpi=120)
        
        if not df.empty:
            monthly = df.groupby(['tipo_usuario', 'month_num', 'month_name'], observed=False)['ride_count'].sum().reset_index()
            monthly.sort_values('month_num', inplace=True)
            
            months_names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
            x = range(1, 13)
            
            for utype, color in [('Miembro Anual', COLOR_MEMBER), ('Usuario Casual', COLOR_CASUAL)]:
                sub_df = monthly[monthly['tipo_usuario'] == utype]
                if not sub_df.empty:
                    full_series = pd.DataFrame({'month_num': x})
                    sub_df = pd.merge(full_series, sub_df, on='month_num', how='left').fillna(0)
                    
                    ax.plot(sub_df['month_num'], sub_df['ride_count'], label=utype, color=color, linewidth=2.5, marker='s', markersize=3.5)
                    ax.fill_between(sub_df['month_num'], sub_df['ride_count'], alpha=0.08, color=color)
            
            ax.set_xticks(x)
            ax.set_xticklabels(months_names)
            
        ax.set_title("Volumen de Viajes Mensuales (Tendencia Anual)", fontsize=9, fontweight='bold', pad=8)
        ax.set_xlabel("Mes", fontsize=7.5)
        ax.set_ylabel("Viajes Totales", fontsize=7.5)
        ax.tick_params(axis='both', labelsize=7.5)
        ax.legend(frameon=False, fontsize=7.5)
        
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        return fig

    # Gráfica 4: Preferencia de Tipo de Bicicleta
    @output
    @render.plot
    def plot_bike_preferences():
        df = filtered_data()
        apply_matplotlib_theme()
        fig, ax = plt.subplots(figsize=(6, 3.2), dpi=120)
        
        if not df.empty:
            bikes = df.groupby(['tipo_usuario', 'rideable_type'], observed=False)['ride_count'].sum().reset_index()
            
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
            
            m_rides = [member_data[member_data['tipo_bici'] == t]['ride_count'].sum() for t in types]
            c_rides = [casual_data[casual_data['tipo_bici'] == t]['ride_count'].sum() for t in types]
            
            ax.bar([pos - width/2 for pos in x], m_rides, width, label='Miembro Anual', color=COLOR_MEMBER, edgecolor='none', alpha=0.9)
            ax.bar([pos + width/2 for pos in x], c_rides, width, label='Usuario Casual', color=COLOR_CASUAL, edgecolor='none', alpha=0.9)
            
            ax.set_xticks(x)
            ax.set_xticklabels(types)
            
        ax.set_title("Preferencias por Tipo de Bicicleta", fontsize=9, fontweight='bold', pad=8)
        ax.set_xlabel("Tipo de Bicicleta", fontsize=7.5)
        ax.set_ylabel("Viajes Totales", fontsize=7.5)
        ax.tick_params(axis='both', labelsize=7.5)
        ax.legend(frameon=False, fontsize=7.5)
        
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        return fig

    # --- LÓGICA DE COPILOT OLVERA AI ---

    # Escucha el envío del formulario de chat y responde
    @chat.on_user_submit
    async def _handle_chat_submit():
        is_empty.set(False)
        ui_messages = list(chat.messages())
        if len(ui_messages) > 10:
            ui_messages = ui_messages[-10:]
            
        # Crear copia limpia de mensajes
        llm_messages = []
        for m in ui_messages:
            role = m.role if hasattr(m, 'role') else m.get('role', '')
            content = m.content if hasattr(m, 'content') else m.get('content', '')
            llm_messages.append({"role": role, "content": content})
            
        # Inyectar el contexto reactivo actual del dashboard en tiempo real
        try:
            with reactive.isolate():
                df = filtered_data()
                total_rides = int(df['ride_count'].sum()) if not df.empty else 0
                
                # Calcular porcentajes reactivos
                if total_rides > 0:
                    member_rides = df[df['tipo_usuario'] == 'Miembro Anual']['ride_count'].sum()
                    casual_rides = df[df['tipo_usuario'] == 'Usuario Casual']['ride_count'].sum()
                    member_pct = (member_rides / total_rides) * 100
                    casual_pct = (casual_rides / total_rides) * 100
                    avg_duration = (df['avg_duration'] * df['ride_count']).sum() / total_rides
                else:
                    member_pct = 0.0
                    casual_pct = 0.0
                    avg_duration = 0.0
                
                active_users = input.user_types()
                active_month = input.months()
                active_days = input.days()
                
            ctx = f"\n\n[CONTEXTO EN TIEMPO REAL DEL DASHBOARD CYCLISTIC - FILTROS ACTIVOS]\n"
            ctx += f"- Segmentos seleccionados: {', '.join(active_users) if active_users else 'Ninguno'}\n"
            ctx += f"- Mes filtrado: {active_month}\n"
            ctx += f"- Días de operación: {', '.join(active_days) if active_days else 'Ninguno'}\n"
            ctx += f"- Viajes Totales Calculados: {total_rides:,}\n"
            ctx += f"- Cuota de Miembros Anuales: {member_pct:.1f}%\n"
            ctx += f"- Cuota de Usuarios Casuales: {casual_pct:.1f}%\n"
            ctx += f"- Duración de Viaje Promedio: {avg_duration:.1f} minutos\n"
            ctx += f"Por favor, integra este contexto en tu análisis si es relevante para responder a la consulta del usuario."
            
            if llm_messages and llm_messages[-1]["role"] == "user":
                llm_messages[-1]["content"] += ctx
        except Exception as e:
            print(f"Error inyectando contexto reactivo en Olvera AI: {e}")

        # Ejecutar streaming de la respuesta usando el modelo configurado
        async_gen = logic.stream_chat_response(
            messages=llm_messages,
            model=providers.DEFAULT_MODEL,
            web_search_enabled=False,
            image_b64=None
        )
        await chat.append_message_stream(async_gen)

    # Evento de clic en los chips de sugerencia rápida
    @reactive.Effect
    @reactive.event(input.suggestion_click)
    async def _handle_suggestion_click():
        prompt = input.suggestion_click()
        if not prompt:
            return
        is_empty.set(False)
        await chat.append_message({"role": "user", "content": prompt})
        
        # Enviar inmediatamente con contexto enriquecido
        try:
            with reactive.isolate():
                df = filtered_data()
                total_rides = int(df['ride_count'].sum()) if not df.empty else 0
                if total_rides > 0:
                    member_rides = df[df['tipo_usuario'] == 'Miembro Anual']['ride_count'].sum()
                    casual_rides = df[df['tipo_usuario'] == 'Usuario Casual']['ride_count'].sum()
                    member_pct = (member_rides / total_rides) * 100
                    casual_pct = (casual_rides / total_rides) * 100
                    avg_duration = (df['avg_duration'] * df['ride_count']).sum() / total_rides
                else:
                    member_pct = 0.0
                    casual_pct = 0.0
                    avg_duration = 0.0
                
                active_users = input.user_types()
                active_month = input.months()
                active_days = input.days()
                
            ctx = f"\n\n[CONTEXTO EN TIEMPO REAL DEL DASHBOARD CYCLISTIC - FILTROS ACTIVOS]\n"
            ctx += f"- Segmentos seleccionados: {', '.join(active_users) if active_users else 'Ninguno'}\n"
            ctx += f"- Mes filtrado: {active_month}\n"
            ctx += f"- Días de operación: {', '.join(active_days) if active_days else 'Ninguno'}\n"
            ctx += f"- Viajes Totales Calculados: {total_rides:,}\n"
            ctx += f"- Cuota de Miembros Anuales: {member_pct:.1f}%\n"
            ctx += f"- Cuota de Usuarios Casuales: {casual_pct:.1f}%\n"
            ctx += f"- Duración de Viaje Promedio: {avg_duration:.1f} minutos\n"
            
            enriched_prompt = prompt + ctx
        except Exception as e:
            print(f"Error inyectando contexto de sugerencia rápida: {e}")
            enriched_prompt = prompt
            
        messages = [{"role": "user", "content": enriched_prompt}]
        async_gen = logic.stream_chat_response(
            messages=messages,
            model=providers.DEFAULT_MODEL,
            web_search_enabled=False,
            image_b64=None
        )
        await chat.append_message_stream(async_gen)

    # Renderizar el Banner de Bienvenida Premium y Chips en Blanco y Negro (Sober)
    @output
    @render.ui
    def welcome_ui():
        if not is_empty.get():
            return ui.div()
        return ui.div(
            ui.div(
                ui.HTML("""
                    <div class="welcome-icon-box">
                        <svg viewBox='0 0 24 24' fill='none' stroke='#ffffff' stroke-width='1.5' style='width:32px;height:32px;'>
                            <path d='M12 2L3 7V17L12 22L21 17V7L12 2Z'/>
                            <path d='M12 22V12'/><path d='M12 12L21 7'/><path d='M12 12L3 7'/>
                        </svg>
                    </div>
                    <h2 class="welcome-title-text">Hola, soy Olvera AI</h2>
                    <p class="welcome-description-text">
                        Soy tu asistente de inteligencia de negocios. Tengo acceso en tiempo real a las métricas, 
                        gráficos de distribución horaria, estacionalidad y preferencias de bicicletas de Cyclistic. 
                        ¿Qué aspecto estratégico deseas auditar hoy?
                    </p>
                """),
                class_="welcome-ui-container"
            ),
            ui.div(
                # Chip 1: Explicar Métricas
                ui.div(
                    ui.HTML("<div class=\"suggestion-box-title\">📊 Explicar Métricas Actuales</div><div class=\"suggestion-box-desc\">Analiza y resume los KPIs y gráficos activos en el dashboard.</div>"),
                    onclick="Shiny.setInputValue('suggestion_click', 'Realiza una auditoría analítica exhaustiva de las métricas y gráficos actuales del dashboard. ¿Qué tendencias críticas observas?', {priority:'event'})",
                    class_="chat-suggestion-box"
                ),
                # Chip 2: Perfiles de Usuario
                ui.div(
                    ui.HTML("<div class=\"suggestion-box-title\">⚡ Perfiles de Segmento</div><div class=\"suggestion-box-desc\">Compara las diferencias de comportamiento clave de miembros vs. casuales.</div>"),
                    onclick="Shiny.setInputValue('suggestion_click', '¿Cuáles son las diferencias críticas de comportamiento (horarios, días, tipos de bicicleta) entre miembros anuales y casuales en base a los datos?', {priority:'event'})",
                    class_="chat-suggestion-box"
                ),
                # Chip 3: Estrategia de Conversión
                ui.div(
                    ui.HTML("<div class=\"suggestion-box-title\">📈 Estrategia de Conversión</div><div class=\"suggestion-box-desc\">Propón campañas de marketing de alta conversión basadas en los hallazgos.</div>"),
                    onclick="Shiny.setInputValue('suggestion_click', 'Sugiere 3 campañas de marketing digital altamente efectivas diseñadas para convertir a los usuarios casuales de Cyclistic en miembros anuales.', {priority:'event'})",
                    class_="chat-suggestion-box"
                ),
                # Chip 4: Estacionalidad de Viajes
                ui.div(
                    ui.HTML("<div class=\"suggestion-box-title\">❄️ Impacto Estacional</div><div class=\"suggestion-box-desc\">Analiza las tendencias estacionales y cómo mitigar los meses fríos.</div>"),
                    onclick="Shiny.setInputValue('suggestion_click', 'Explica la estacionalidad mensual observada en los viajes de Cyclistic. ¿Cómo deberíamos reaccionar ante la brecha invernal?', {priority:'event'})",
                    class_="chat-suggestion-box"
                ),
                class_="suggestion-chips-grid"
            ),
            style="max-width:720px; margin:0 auto;"
        )

    # Renderizar el pie de página de estado del chat
    @output
    @render.ui
    def chat_toolbar_ui():
        return ui.HTML("""
            <div style='border-top:1px solid rgba(255, 255, 255, 0.08); padding:10px 6px 0; margin-top:12px; display:flex; align-items:center; gap:8px; flex-wrap:wrap;'>
                <span style='font-size:0.75rem; color:#ffffff; font-weight:700; letter-spacing:0.5px;'>OLVERA AI SUITE</span>
                <span style='font-size:0.75rem; color:rgba(255, 255, 255, 0.2);'>|</span>
                <span style='font-size:0.75rem; color:#9ca3af;'>Engine: Gemini 3 Flash &bull; Contexto reactivo del dashboard inyectado en cada consulta</span>
            </div>
        """)

# Instanciar aplicación Shiny
app = App(app_ui, server)
