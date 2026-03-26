@app.route('/students')
@login_required
def students():
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))

        students_raw = []
        program_rows = []
        try:
            # Get all students and their information
            students_raw = conn.execute('''
                SELECT id, name, index_number, gender, age, faculty, department, programme, 
                       hall_of_residence, contact, email, parent_contact, created_at, 
                       case_number, global_id, updated_at, last_synced_at
                FROM Student 
                WHERE is_deleted = 0
                ORDER BY name
            ''').fetchall()

            # Get unique programs for the filter
            program_rows = conn.execute(
                "SELECT DISTINCT programme FROM Student WHERE programme IS NOT NULL AND is_deleted = 0").fetchall()
        except Exception as e:
            print(f"[STUDENTS] Error getting students: {e}")
            students_raw = []
            program_rows = []
        finally:
            try:
                conn.close()
            except Exception:
                pass

        # Map to specific identifiers as per technical spec
        students = []
        for student in students_raw:
            student_dict = dict(student)
            
            # GTEC REQUIRED: Standardize name to initials at runtime
            student_dict['name'] = name_to_initials(student_dict.get('name', 'User'))
            
            # 1. Case ID (GCC-2026-####)
            student_dict['case_id'] = student_dict.get('case_number') or f"GCC-{datetime.now().year}-{student_dict.get('id', 0):04d}"
            
            # 2. Professional ID (NW-2026-####) - Use initials
            initials = student_dict['name']
            student_dict['professional_id'] = f"{initials}-{datetime.now().year}-{student_dict.get('id', 0):04d}"
            
            # Decrypt sensitive fields
            for field in STUDENT_SENSITIVE_FIELDS:
                if field in student_dict and student_dict[field]:
                    student_dict[field] = decrypt_field(student_dict[field])
                
            students.append(student_dict)

        # Convert Row objects to strings
        programs = [row['programme']
                    for row in program_rows] if program_rows else []

        return render_template('students.html', students=students, programs=programs)
    except Exception as e:
        print(f"[STUDENTS] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading students. Please try again.', 'error')
        return redirect(url_for('dashboard'))
