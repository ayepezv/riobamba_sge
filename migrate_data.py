import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def run_migration():
    with connection.cursor() as cursor:
        print("Starting data migration...")

        # 1. Proceso (fi_proceso -> pl_proceso)
        print("Migrating Proceso...")
        cursor.execute("""
            INSERT INTO pl_proceso (id, codigo, nombre)
            SELECT id, codigo, nombre FROM fi_proceso
            ON CONFLICT (id) DO NOTHING;
        """)

        # 2. Direccion (fi_direccion -> pl_direccion)
        print("Migrating Direccion...")
        cursor.execute("""
            INSERT INTO pl_direccion (id, codigo, nombre, proceso_id)
            SELECT id, codigo, nombre, proceso_id FROM fi_direccion
            ON CONFLICT (id) DO NOTHING;
        """)

        # 3. Unidad (fi_unidad -> pl_unidad)
        print("Migrating Unidad...")
        cursor.execute("""
            INSERT INTO pl_unidad (id, codigo, nombre, es_movimiento, direccion_id)
            SELECT id, codigo, nombre, es_movimiento, direccion_id FROM fi_unidad
            ON CONFLICT (id) DO NOTHING;
        """)

        # 4. Fuente (fi_fuente -> pr_fuente)
        print("Migrating Fuente...")
        cursor.execute("""
            INSERT INTO pr_fuente (id, codigo, nombre)
            SELECT id, codigo, nombre FROM fi_fuente
            ON CONFLICT (id) DO NOTHING;
        """)

        # 5. Clasificador (fi_clasificador -> pr_clasificador)
        # Handle recursive structure? Since we copy ID to ID, order doesn't strict matter for Insert, 
        # but FK constraints exists. However, if we insert all rows, referencing a parent ID that is also inserted in same transaction usually works in Postgres unless deferred.
        # But to be safe, we disable constraints or hope for the best.
        # Actually, self-referencing FKs in same table: valid if parent exists.
        # Order by NIVEL ensures parents (Level 1) inserted before children (Level 2).
        print("Migrating Clasificador...")
        cursor.execute("""
            INSERT INTO pr_clasificador (id, codigo, codigo_visual, nombre, descripcion, nivel, tipo, es_imputable, agrupador, padre_id)
            SELECT id, codigo, NULL, nombre, descripcion, nivel, tipo, es_imputable, agrupador, padre_id 
            FROM fi_clasificador
            ORDER BY nivel ASC
            ON CONFLICT (id) DO NOTHING;
        """)

        # 6. Presupuesto (fi_presupuesto -> pr_presupuesto)
        print("Migrating Presupuesto...")
        cursor.execute("""
            INSERT INTO pr_presupuesto (id, anio, partida_concatenada, asignacion_inicial, reformas, devengado, certificado, comprometido, clasificador_id, fuente_id, unidad_id)
            SELECT id, anio, partida_concatenada, asignacion_inicial, reformas, devengado, certificado, comprometido, clasificador_id, fuente_id, unidad_id
            FROM fi_presupuesto
            ON CONFLICT (id) DO NOTHING;
        """)
        
        # 7. PAC (financiero_pac -> pl_pac)
        print("Migrating PAC...")
        cursor.execute("""
            INSERT INTO pl_pac (id, anio, descripcion, estado, fecha_aprobacion, created_at)
            SELECT id, anio, descripcion, estado, fecha_aprobacion, created_at
            FROM financiero_pac
            ON CONFLICT (id) DO NOTHING;
        """)

        # 8. PACLinea (financiero_paclinea -> pl_pac_linea)
        # Note: Mapping old 'cuatrimestre' char to new boolean c1, c2, c3?
        # apps/financiero/models.py PACLinea had 'cuatrimestre' (char 1,2,3)
        # apps/planificacion/models.py PACLinea has c1, c2, c3 (bool)
        # I need CASE statement.
        print("Migrating PACLinea...")
        cursor.execute("""
            INSERT INTO pl_pac_linea (id, cpc, tipo_compra, detalle, cantidad, costo_unitario, monto_total, procedimiento_sugerido, codigo_original, pac_id, partida_id, c1, c2, c3)
            SELECT 
                id, cpc, tipo_compra, detalle, cantidad, costo_unitario, monto_total, procedimiento_sugerido, codigo_original, pac_id, partida_id,
                c1, c2, c3
            FROM financiero_paclinea
            ON CONFLICT (id) DO NOTHING;
        """)

        # Reset sequences (Postgres)
        # To avoid "duplicate key value" on next insert.
        print("Resetting sequences...")
        tables_seq = [
            'pl_proceso', 'pl_direccion', 'pl_unidad', 'pl_pac', 'pl_pac_linea',
            'pr_fuente', 'pr_clasificador', 'pr_presupuesto'
        ]
        for t in tables_seq:
            try:
                cursor.execute(f"SELECT setval(pg_get_serial_sequence('{t}', 'id'), coalesce(max(id),0) + 1, false) FROM {t};")
            except Exception as e:
                print(f"Warning resetting sequence for {t}: {e}")

        print("Migration complete!")

if __name__ == '__main__':
    run_migration()
