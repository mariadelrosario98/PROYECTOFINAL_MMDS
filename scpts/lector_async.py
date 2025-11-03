import asyncio
import aiofiles
import os

# Ruta al archivo de datos
FILE_PATH = r"C:\Users\ASUS\Documents\Maestria Ciencia de los Datos\TERCER SEMESTRE\MINERIA DE GRANDES VOLUMENES INFO\PROYECTO FINAL\DATA\soc-LiveJournal1.txt"

async def read_large_file_async(file_path):
    """
    Lee un archivo línea por línea de forma asíncrona, saltando los metadatos,
    y procesa cada arista (conexión).
    """
    try:
        print(f"Iniciando procesamiento asíncrono del archivo: {file_path}")
        
        async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
            line_count = 0
                        async for line in f:
                line_count += 1
                
                if line.startswith('#'):
                    if line_count == 4:
                    continue
                
                try:
                    parts = line.split()
                    
                    if len(parts) == 2:
                        from_node = int(parts[0])
                        to_node = int(parts[1])
                        
                        if line_count <= 9: 
                            print(f"ARISTA {line_count - 4}: {from_node} -> {to_node}")
                        
                except ValueError:
¿                    pass
            
            print(f"\n Procesamiento completado. Total de líneas leídas (incl. meta): {line_count}")

    except FileNotFoundError:
        print(f"Error: El archivo no se encontró en la ruta: {file_path}")
    except Exception as e:
        print(f"Ocurrió un error inesperado durante la lectura: {e}")


def main():
    asyncio.run(read_large_file_async(FILE_PATH))

if __name__ == "__main__":
    main()