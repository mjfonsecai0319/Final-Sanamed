import psycopg2
from dotenv import load_dotenv

load_dotenv()

def fix_sequences():
    conn = psycopg2.connect("postgresql://usuario:fIu8PbJJDb6VgSraMXDX4jj5EFzgFdfu@dpg-d3ep0ql6ubrc739dqg9g-a.virginia-postgres.render.com:5432/postsanamed")
    cur = conn.cursor()
    
    # Tablas y sus columnas ID
    tables = [
        ('usuarios', 'id_usuario'),
        ('profesionales', 'id_profesional'),
        ('consultas', 'id_consulta'),
        ('emociones', 'id_emocion'),
        ('administradores', 'id_administrador'),
        ('familias_gratitud', 'id_gratitud'),
        ('perfiles', 'id_perfil')
    ]
    
    print("🔄 Reseteando secuencias...")
    
    for table, id_column in tables:
        try:
            # Obtener el máximo ID actual
            cur.execute(f"SELECT COALESCE(MAX({id_column}), 0) FROM {table}")
            max_id = cur.fetchone()[0]
            
            # Nombre de la secuencia (PostgreSQL naming convention)
            sequence_name = f"{table}_{id_column}_seq"
            
            # Resetear la secuencia al máximo ID + 1
            cur.execute(f"SELECT setval('{sequence_name}', {max_id + 1}, false)")
            
            # Verificar el nuevo valor
            cur.execute(f"SELECT nextval('{sequence_name}')")
            next_val = cur.fetchone()[0]
            
            print(f"✅ {table}: Secuencia ajustada a {max_id + 1}, próximo ID: {next_val}")
            
        except Exception as e:
            print(f"⚠️  Error en {table}: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    print("🎉 ¡Secuencias reseteadas correctamente!")

if __name__ == '__main__':
    fix_sequences()