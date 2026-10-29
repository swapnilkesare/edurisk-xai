"""
Database Migration: Add PRN and Institutional Fields to Students Table
Safely applies backward-compatible columns to edurisk.db without dropping tables or losing data.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "edurisk.db")

def migrate():
    print(f"Connecting to database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    existing_cols = [r[1] for r in cur.execute("PRAGMA table_info(students)").fetchall()]
    print(f"Existing columns in 'students': {existing_cols}")

    new_cols = [
        ("prn", "VARCHAR(64)"),
        ("email", "VARCHAR(128)"),
        ("batch_year", "VARCHAR(32) DEFAULT '2024–2028'"),
        ("division", "VARCHAR(16) DEFAULT 'A'"),
        ("enrollment_status", "VARCHAR(32) DEFAULT 'Active'"),
        ("academic_history", "TEXT")
    ]

    for col_name, col_type in new_cols:
        if col_name not in existing_cols:
            cur.execute(f"ALTER TABLE students ADD COLUMN {col_name} {col_type}")
            print(f"  + Added column: {col_name} ({col_type})")
        else:
            print(f"  - Column already exists: {col_name}")

    # Backfill PRN from student_identifier where prn is NULL
    cur.execute("UPDATE students SET prn = UPPER(TRIM(student_identifier)) WHERE prn IS NULL")
    
    # Create index on PRN for fast institutional lookup
    cur.execute("CREATE INDEX IF NOT EXISTS idx_students_prn ON students(prn)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_students_org_prn ON students(organization_id, prn)")

    conn.commit()

    # Verify migration results
    updated_cols = [r[1] for r in cur.execute("PRAGMA table_info(students)").fetchall()]
    print(f"\nMigration successful. Updated columns in 'students':\n{updated_cols}")
    
    cur.execute("SELECT id, student_identifier, prn, name, organization_id, enrollment_status FROM students")
    rows = cur.fetchall()
    print(f"\nTotal existing student records: {len(rows)}")
    for r in rows:
        print(f"  ID={r[0]}: PRN={r[2]} ({r[1]}), Name={r[3]}, Org={r[4]}, Status={r[5]}")

    conn.close()

if __name__ == "__main__":
    migrate()
