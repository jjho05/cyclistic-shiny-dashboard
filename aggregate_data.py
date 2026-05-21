#!/usr/bin/env python3
import os
import pandas as pd
import gc

def main():
    base_dir = '/Users/lic.ing.jesusolvera/Documents/PCD CLAUDIA/cyclistic'
    input_csv = os.path.join(base_dir, 'cyclistic_consolidado.csv')
    output_csv = os.path.join(base_dir, 'cyclistic_aggregated.csv')
    
    print("=== INICIANDO AGREGACIÓN DE DATOS PARA SHINY ===")
    if not os.path.exists(input_csv):
        print(f"[ERROR] No se encontró el archivo consolidado en {input_csv}")
        return
        
    print(f"Leyendo archivo grande {input_csv}...")
    
    # Especificar tipos para minimizar uso de memoria al leer
    dtypes = {
        'rideable_type': 'category',
        'tipo_usuario': 'category',
        'day_of_week': 'category',
        'hour': 'int8'
    }
    
    # Leer el archivo por partes/chunks para optimizar memoria en máquinas con menos RAM
    chunks = []
    chunksize = 200000
    
    # Mapeo de meses para clasificación estacional y temporal en español
    month_mapping = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    for i, chunk in enumerate(pd.read_csv(input_csv, dtype=dtypes, chunksize=chunksize)):
        print(f"  Procesando chunk {i+1}...")
        # Convertir started_at a datetime
        chunk['started_at'] = pd.to_datetime(chunk['started_at'])
        
        # Extraer número y nombre de mes
        chunk['month_num'] = chunk['started_at'].dt.month.astype('int8')
        chunk['month_name'] = chunk['month_num'].map(month_mapping).astype('category')
        
        # Agrupar este chunk para reducir espacio inmediatamente
        grouped_chunk = chunk.groupby(
            ['tipo_usuario', 'day_of_week', 'hour', 'rideable_type', 'month_num', 'month_name'],
            observed=False
        ).agg(
            ride_count=('ride_length', 'count'),
            total_duration=('ride_length', 'sum')
        ).reset_index()
        
        chunks.append(grouped_chunk)
        
    print("Consolidando todos los chunks agrupados...")
    df_all = pd.concat(chunks, ignore_index=True)
    del chunks
    gc.collect()
    
    print("Realizando la agregación final...")
    df_final = df_all.groupby(
        ['tipo_usuario', 'day_of_week', 'hour', 'rideable_type', 'month_num', 'month_name'],
        observed=False
    ).agg(
        ride_count=('ride_count', 'sum'),
        total_duration=('total_duration', 'sum')
    ).reset_index()
    
    # Calcular promedio de duración
    df_final['avg_duration'] = (df_final['total_duration'] / df_final['ride_count']).round(2)
    # Eliminar columna auxiliar de duración total
    df_final.drop(columns=['total_duration'], inplace=True)
    
    # Ordenar por número de mes, día de la semana y hora para que las gráficas sean ordenadas por defecto
    week_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    df_final['day_of_week'] = pd.Categorical(df_final['day_of_week'], categories=week_order, ordered=True)
    df_final.sort_values(by=['month_num', 'day_of_week', 'hour'], inplace=True)
    
    print(f"Guardando archivo agregado optimizado en {output_csv}...")
    df_final.to_csv(output_csv, index=False)
    
    size_mb = os.path.getsize(output_csv) / (1024 * 1024)
    print(f"=== ¡ÉXITO! Archivo agregado guardado: {size_mb:.2f} MB ({len(df_final):,} filas) ===")

if __name__ == '__main__':
    main()
