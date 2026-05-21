#!/usr/bin/env python3
import os
import glob
import pandas as pd

def main():
    base_dir = '/Users/lic.ing.jesusolvera/Documents/PCD CLAUDIA/cyclistic'
    
    # 1. Encontrar todos los archivos CSV en el directorio
    csv_pattern = os.path.join(base_dir, '*tripdata.csv')
    csv_files = sorted(glob.glob(csv_pattern))
    
    print("=== INICIANDO FASE 1: CONSOLIDACIÓN DE DATOS ===")
    print(f"Archivos CSV encontrados ({len(csv_files)}):")
    for f in csv_files:
        print(f"  - {os.path.basename(f)}")
        
    if not csv_files:
        print("[ERROR] No se encontraron archivos CSV en el directorio.")
        return
        
    # Columnas necesarias para optimizar memoria
    usecols = ['rideable_type', 'started_at', 'ended_at', 'member_casual']
    dtypes = {
        'rideable_type': 'category',
        'member_casual': 'category'
    }
    
    dfs = []
    for filepath in csv_files:
        filename = os.path.basename(filepath)
        print(f"Cargando y procesando {filename} (optimizando memoria)...")
        # Cargar solo columnas esenciales
        df_month = pd.read_csv(filepath, usecols=usecols, dtype=dtypes)
        dfs.append(df_month)
        
    print("\nConcatenando todos los meses en un único DataFrame...")
    df = pd.concat(dfs, ignore_index=True)
    del dfs
    import gc
    gc.collect()
    total_raw_rows = len(df)
    print(f"Total de registros cargados (bruto): {total_raw_rows:,}")
    
    print("\n=== INICIANDO FASE 2: LIMPIEZA Y TRANSFORMACIÓN ===")
    # Eliminar nulos en columnas críticas
    df.dropna(subset=usecols, inplace=True)
    
    # Convertir a datetime
    print("Convirtiendo columnas de fecha/hora (esto puede tomar unos momentos)...")
    df['started_at'] = pd.to_datetime(df['started_at'])
    df['ended_at'] = pd.to_datetime(df['ended_at'])
    
    # Calcular duración del viaje en minutos (ride_length)
    print("Calculando duración de los viajes (ride_length en minutos)...")
    df['ride_length'] = ((df['ended_at'] - df['started_at']).dt.total_seconds() / 60.0).round(2)
    
    # Limpieza: eliminar viajes con duración menor o igual a 0, o mayores a 24 horas (1440 minutos)
    print("Filtrando viajes erróneos (duración <= 0 min o > 24 horas)...")
    df_clean = df[(df['ride_length'] > 0) & (df['ride_length'] <= 1440)].copy()
    del df
    gc.collect()
    
    total_clean_rows = len(df_clean)
    rows_removed = total_raw_rows - total_clean_rows
    print(f"Registros limpios: {total_clean_rows:,} ({total_clean_rows / total_raw_rows * 100:.2f}%)")
    print(f"Registros eliminados por limpieza: {rows_removed:,}")
    
    # Extraer variables de tiempo
    print("Extrayendo variables temporales (Día de la semana, Hora)...")
    # Mapeo a español para presentación premium
    day_mapping = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    df_clean['day_name_en'] = df_clean['started_at'].dt.day_name()
    df_clean['day_of_week'] = df_clean['day_name_en'].map(day_mapping)
    df_clean['hour'] = df_clean['started_at'].dt.hour
    
    # Definir el orden estándar de la semana
    week_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    df_clean['day_of_week'] = pd.Categorical(df_clean['day_of_week'], categories=week_order, ordered=True)
    
    # Mapear tipos de usuarios en español para legibilidad en gráficas
    user_mapping = {
        'member': 'Miembro Anual',
        'casual': 'Usuario Casual'
    }
    df_clean['tipo_usuario'] = df_clean['member_casual'].map(user_mapping)
    df_clean['tipo_usuario'] = pd.Categorical(df_clean['tipo_usuario'], categories=['Miembro Anual', 'Usuario Casual'], ordered=True)
    
    print("\n=== INICIANDO FASE 3: ANÁLISIS DESCRIPTIVO ===")
    
    # Estadísticas generales de duración de viaje
    print("\n--- Estadísticas de Duración del Viaje (Minutos) ---")
    stats_overall = df_clean['ride_length'].describe()
    print(f"General - Media: {stats_overall['mean']:.2f} min | Mediana: {df_clean['ride_length'].median():.2f} min | Max: {stats_overall['max']:.2f} min")
    
    for user_type in ['Miembro Anual', 'Usuario Casual']:
        user_df = df_clean[df_clean['tipo_usuario'] == user_type]
        stats_user = user_df['ride_length'].describe()
        median_user = user_df['ride_length'].median()
        print(f"{user_type} - Media: {stats_user['mean']:.2f} min | Mediana: {median_user:.2f} min | Max: {stats_user['max']:.2f} min | Total Viajes: {len(user_df):,}")

    # Nota: El análisis gráfico y tableros interactivos se realizarán directamente en Power BI.
    
    # ----------------------------------------------------
    # FASE 5: GUARDAR ARCHIVO CONSOLIDADO Y LIMPIO
    # ----------------------------------------------------
    print("\n=== INICIANDO FASE 5: EXPORTACIÓN DE ARCHIVOS CSV ===")
    
    # Eliminar columnas redundantes/intermedias en inglés para reducir el tamaño del archivo
    # - member_casual   → reemplazada por tipo_usuario (en español)
    # - day_name_en     → reemplazada por day_of_week (en español)
    # - ended_at        → ya tenemos ride_length que contiene la duración calculada
    cols_to_drop = ['member_casual', 'day_name_en', 'ended_at']
    df_export = df_clean.drop(columns=[c for c in cols_to_drop if c in df_clean.columns])
    
    print(f"Columnas en el archivo final ({len(df_export.columns)}): {list(df_export.columns)}")
    print(f"Filas totales: {len(df_export):,}")
    
    # 1. Guardar CSV Estándar (punto decimal, coma como separador de columnas)
    output_csv_path = os.path.join(base_dir, 'cyclistic_consolidado.csv')
    print(f"\nGuardando el conjunto de datos estándar en: {output_csv_path}...")
    df_export.to_csv(output_csv_path, index=False, chunksize=100000)
    size_mb = os.path.getsize(output_csv_path) / (1024 * 1024)
    print(f"  [OK] Archivo CSV estándar guardado: {size_mb:.1f} MB")
    
    # 2. Guardar CSV Regional (coma decimal, punto y coma como separador de columnas)
    # Ideal para sistemas en español/latinoamérica que abren directamente en Excel/Power BI sin configurar locale
    output_csv_regional = os.path.join(base_dir, 'cyclistic_consolidado_regional.csv')
    print(f"Guardando el conjunto de datos regional en: {output_csv_regional}...")
    df_export.to_csv(output_csv_regional, sep=';', decimal=',', index=False, chunksize=100000)
    size_mb_reg = os.path.getsize(output_csv_regional) / (1024 * 1024)
    print(f"  [OK] Archivo CSV regional guardado: {size_mb_reg:.1f} MB")
    
    print("\n==============================================")
    print("¡PROCESAMIENTO, ANÁLISIS Y CONSOLIDACIÓN DE DATOS COMPLETADOS!")
    print("==============================================")

if __name__ == '__main__':
    main()
