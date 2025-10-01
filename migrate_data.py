import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_ordered():
    # Conexiones
    conn_local = psycopg2.connect("dbname=postsanamed user=usuario password=sanamed host=localhost")
    conn_local.autocommit = True
    
    conn_render = psycopg2.connect("postgresql://usuario:fIu8PbJJDb6VgSraMXDX4jj5EFzgFdfu@dpg-d3ep0ql6ubrc739dqg9g-a.virginia-postgres.render.com:5432/postsanamed")
    conn_render.autocommit = True
    
    # ORDEN CORRECTO: Primero tablas sin FKs, luego las que dependen de ellas
    tables_order = [
        'perfiles',      # Sin dependencias
        'usuarios',      # Depende de perfiles
        'administradores', # Sin dependencias  
        'profesionales', # Sin dependencias
        'emociones',     # Depende de usuarios
        'familias_gratitud', # Depende de usuarios
        'consultas',     # Depende de usuarios y profesionales
        'profesionales_usuarios' # Depende de usuarios y profesionales
    ]
    
    try:
        print("🔄 Iniciando migración ordenada...")
        
        for table in tables_order:
            print(f"\n🚀 Migrando tabla: {table}")
            
            # Obtener datos de tabla local
            cur_local = conn_local.cursor()
            cur_local.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table)))
            rows = cur_local.fetchall()
            
            # Obtener nombres de columnas
            cur_local.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table,))
            columns = [col[0] for col in cur_local.fetchall()]
            
            # Insertar en Render
            if rows:
                cur_render = conn_render.cursor()
                
                # Preparar inserción
                placeholders = ', '.join(['%s'] * len(columns))
                columns_str = ', '.join(columns)
                
                inserted_count = 0
                for row in rows:
                    try:
                        cur_render.execute(
                            sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                                sql.Identifier(table),
                                sql.SQL(columns_str),
                                sql.SQL(placeholders)
                            ), row
                        )
                        inserted_count += 1
                    except Exception as e:
                        print(f"  ❌ Error en fila: {e}")
                        continue
                
                conn_render.commit()
                cur_render.close()
                print(f"  ✅ {inserted_count}/{len(rows)} registros migrados")
            else:
                print(f"  ⏭️  Tabla {table} vacía")
        
        print(f"\n🎉 ¡Migración ordenada completada!")
        
    except Exception as e:
        print(f"❌ Error durante migración: {e}")
    finally:
        conn_local.close()
        conn_render.close()

if __name__ == '__main__':
    migrate_ordered()