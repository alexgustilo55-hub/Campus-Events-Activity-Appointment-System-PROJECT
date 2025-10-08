from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql,os

app = Flask(__name__)
app.secret_key = "12345"
app.config['UPLOAD_FOLDER'] = "static/img_profile/"
app.config['EVENT_UPLOADS'] = "static/img_events/"


def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",       
        password="Flaskframework",       
        database="ecela",
        cursorclass=pymysql.cursors.DictCursor
    )
#------------------- Main Page ------------------#


@app.route('/')
def main():
    return render_template("login.html")


#--------------------------- User Register Process -----------------------#

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role')
        gender = request.form.get('gender')
        fullname = request.form.get('fullname')
        phone = request.form.get('phone')
        birthday = request.form.get('birthday')
        email = request.form.get('email')
        address = request.form.get('address')
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()

        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_email = cursor.fetchone()

        cursor.execute("SELECT * FROM users WHERE phone = %s", (phone,))
        existing_phone = cursor.fetchone()

        if existing_user:
            flash("Username already taken!", "danger")
            return render_template("register.html")  
        elif existing_email:
            flash("Email already registered!", "danger")
            return render_template("register.html")  
        elif existing_phone:
            flash("Phone number already registered!", "danger")
            return render_template("register.html")  
        else:
            cursor.execute("""
                INSERT INTO users 
                (email, username, password, phone, full_name, gender, role, address, birthday) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (email, username, password, phone, fullname, gender, role, address, birthday))
            
            conn.commit()
            flash("Registration successful!", "success")
            cursor.close()
            conn.close()
            return redirect(url_for('login'))

        cursor.close()
        conn.close()

    return render_template("register.html")

#------------------------------- User Login Process -------------------------------------#

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s AND role=%s", (username, password,role))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['role'] = user['role']
            session['username'] = user['username']
            flash("Login successful!", "success")

            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'student':
                return redirect(url_for('home'))
            elif user['role'] == 'faculty':
                return redirect(url_for('home'))
            elif user['role'] == 'organizer':
                if user['organizer_type'] == 'faculty':
                    return redirect(url_for('organizer_home'))
            else:
                return redirect(url_for('login'))          
        else:
            flash("Invalid username or password", "error")

    return render_template("login.html")


#------------------------------------- Admin Home Page -----------------------------------#


@app.route('/admin_dashboard')
def admin_dashboard():
    if "username" in session:
        if "username" in session:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
                user = cursor.fetchone()  
                cursor.execute("SELECT * FROM events")
                events = cursor.fetchall()
        conn.close()
        return render_template("admin_home.html", user=user, events = events)  
    else:
        return redirect(url_for("login"))
    
#------------------------------------- Admin Information -----------------------------------#

@app.route('/admin_info')
def admin_info():
    if "username" in session:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
            user = cursor.fetchone()
        conn.close()
        return render_template("admin_information.html", user=user)
    else:
        return redirect(url_for("login"))
    
#-------------------------------------- Admin Update Password ------------------------------#

@app.route('/admin_update_password', methods=['GET', 'POST'])
def admin_update_password():
    if "username" not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if request.method == "POST":
        email = request.form.get("email")
        current_password = request.form.get("current_password") 
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        with conn.cursor() as cursor:
            
            cursor.execute("SELECT email, password FROM users WHERE username=%s", (session["username"],))
            result = cursor.fetchone()

            if result is None:
                flash("User not found.", "danger")
                conn.close()
                return redirect(url_for("admin_update_password"))

            db_email = result["email"]        
            db_password = result["password"]  

            if email != db_email:
                flash("Email does not match.", "danger")
                conn.close()
                return redirect(url_for("admin_update_password"))

            if current_password != db_password:
                flash("Incorrect current password.", "danger")
                conn.close()
                return redirect(url_for("admin_update_password"))

            if new_password != confirm_password:
                flash("New passwords do not match.", "danger")
                conn.close()
                return redirect(url_for("admin_update_password"))

            cursor.execute("UPDATE users SET password=%s WHERE username=%s", (new_password, session["username"]))
            conn.commit()

        conn.close()
        flash("Password updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
        user = cursor.fetchone()
    conn.close()
    return render_template("admin_changepass.html", user=user)



#-------------------------------------- Admin Manage Events ----------------------------------------#

@app.route('/manage_events')
def manage_events():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
    user = cursor.fetchone()
    print("DEBUG user:", user)   

    cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
    events = cursor.fetchall()
    print("DEBUG events:", events)   

    conn.close()
    return render_template("admin_manage_event.html", user=user, events=events)


#-------------------------------------- Admin Delete Events ----------------------------------------#

@app.route('/delete_event/<int:event_id>', methods=['GET'])
def delete_event(event_id):
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM events WHERE event_id = %s", (event_id,))
    conn.commit()

    conn.close()
    flash("Event deleted successfully!", "success")
    return redirect(url_for("manage_events"))


#-------------------------------------- Admin Update Events ----------------------------------------#


@app.route('/update_event/<int:event_id>', methods=['GET', 'POST'])
def update_event(event_id):
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM events WHERE event_id=%s", (event_id,))
    event = cursor.fetchone()

    if not event:
        conn.close()
        flash("Event not found!", "danger")
        return redirect(url_for("manage_events"))

    if request.method == 'POST':
        
        name = request.form.get('event_name')
        event_type = request.form.get('event_type')
        description = request.form.get('description')
        event_date = request.form.get('event_date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        location = request.form.get('location')

        event_image_filename = event['event_image']  
        if 'event_image' in request.files:
            file = request.files['event_image']
            if file and file.filename != '':
                filename = file.filename
                upload_path = os.path.join(app.config['EVENT_UPLOADS'], filename)
                file.save(upload_path)
                event_image_filename = filename  

        query = """
            UPDATE events
            SET event_name=%s, event_type=%s, description=%s, 
                event_date=%s, start_time=%s, end_time=%s, 
                location=%s, event_image=%s
            WHERE event_id=%s
        """
        cursor.execute(query, (name, event_type, description, event_date,
                               start_time, end_time, location, event_image_filename, event_id))
        conn.commit()
        conn.close()

        flash("Event updated successfully!", "success")
        return redirect(url_for("manage_events"))

    conn.close()
   
    return render_template("admin_update_event.html", user=user, event=event)

#-------------------------------------- Organizer Home Page ----------------------------------------#

@app.route('/organizer_home')
def organizer_home():
    if "username" in session:
        if "username" in session:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
                user = cursor.fetchone()  
                cursor.execute("SELECT * FROM events")
                events = cursor.fetchall()
        conn.close()
        return render_template("org_home.html", user=user, events = events)  
    else:
        return redirect(url_for("login"))
    
#------------------------------------- Organizer Information -----------------------------------#

@app.route('/organizer_info')
def organizer_info():
    if "username" in session:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
            user = cursor.fetchone()
        conn.close()
        return render_template("org_information.html", user=user)
    else:
        return redirect(url_for("login"))
    
#-------------------------------------- Organizer Update Password ------------------------------#

@app.route('/organizer_update_password', methods=['GET', 'POST'])
def organizer_update_password():
    if "username" not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if request.method == "POST":
        email = request.form.get("email")
        current_password = request.form.get("current_password") 
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        with conn.cursor() as cursor:
            
            cursor.execute("SELECT email, password FROM users WHERE username=%s", (session["username"],))
            result = cursor.fetchone()

            if result is None:
                flash("User not found.", "danger")
                conn.close()
                return redirect(url_for("organizer_update_password"))

            db_email = result["email"]        
            db_password = result["password"]  

            if email != db_email:
                flash("Email does not match.", "danger")
                conn.close()
                return redirect(url_for("organizer_update_password"))

            if current_password != db_password:
                flash("Incorrect current password.", "danger")
                conn.close()
                return redirect(url_for("organizer_update_password"))

            if new_password != confirm_password:
                flash("New passwords do not match.", "danger")
                conn.close()
                return redirect(url_for("organizer_update_password"))

            cursor.execute("UPDATE users SET password=%s WHERE username=%s", (new_password, session["username"]))
            conn.commit()

        conn.close()
        flash("Password updated successfully!", "success")
        return redirect(url_for("organizer_home"))
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
        user = cursor.fetchone()
    conn.close()
    return render_template("org_changepass.html", user=user)

#-------------------------------------- Organizer Create Events -----------------------------------#

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
        user = cursor.fetchone()
    conn.close()

    if request.method == 'POST':
        name = request.form.get('event_name')
        event_type = request.form.get('event_type')
        description = request.form.get('description')
        event_date = request.form.get('event_date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        location = request.form.get('location')

        
        event_image_filename = None
        if 'event_image' in request.files:
            file = request.files['event_image']
            if file and file.filename != '':
                filename = file.filename
                upload_path = os.path.join(app.config['EVENT_UPLOADS'], filename)
                file.save(upload_path)
                event_image_filename = filename  

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO events (event_name, event_type, description, event_date, start_time, end_time, location, event_image)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, event_type, description, event_date, start_time, end_time, location, event_image_filename))
        conn.commit()
        conn.close()

        flash("Successfully created event!", "success")
        return redirect(url_for("organizer_home"))

    return render_template("org_create_event.html", user=user)

#-------------------------------------- Organizer Manage Events ----------------------------------------#

@app.route('/org_manage_events')
def organizer_manage_events():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get organizer info
    cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
    user = cursor.fetchone()

    # Get all events (you can also filter only events created by them if you add a 'created_by' column)
    cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
    events = cursor.fetchall()

    conn.close()
    return render_template("org_manage_event.html", user=user, events=events)

#-------------------------------------- Organizer Delete Event ----------------------------------------#

@app.route('/org_delete_event/<int:event_id>', methods=['GET'])
def org_delete_event(event_id):
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM events WHERE event_id = %s", (event_id,))
    conn.commit()
    conn.close()

    flash("Event deleted successfully!", "success")
    return redirect(url_for("org_manage_events"))

#-------------------------------------- Organizer Update Event ----------------------------------------#

@app.route('/org_update_event/<int:event_id>', methods=['GET', 'POST'])
def organizer_update_events(event_id):
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Get user and event details
    cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM events WHERE event_id=%s", (event_id,))
    event = cursor.fetchone()

    if not event:
        conn.close()
        flash("Event not found!", "danger")
        return redirect(url_for("organizer_manage_events"))

    if request.method == 'POST':
        name = request.form.get('event_name')
        event_type = request.form.get('event_type')
        description = request.form.get('description')
        event_date = request.form.get('event_date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        location = request.form.get('location')

        event_image_filename = event['event_image']
        if 'event_image' in request.files:
            file = request.files['event_image']
            if file and file.filename != '':
                filename = file.filename
                upload_path = os.path.join(app.config['EVENT_UPLOADS'], filename)
                file.save(upload_path)
                event_image_filename = filename

        query = """
            UPDATE events
            SET event_name=%s, event_type=%s, description=%s,
                event_date=%s, start_time=%s, end_time=%s,
                location=%s, event_image=%s
            WHERE event_id=%s
        """
        cursor.execute(query, (name, event_type, description, event_date,
                               start_time, end_time, location, event_image_filename, event_id))
        conn.commit()
        conn.close()

        flash("Event updated successfully!", "success")
        return redirect(url_for("organizer_manage_events"))

    conn.close()
    return render_template("org_update_event.html", user=user, event=event)

#--------------------------------------- User Home Page --------------------------------------------#

@app.route('/home')
def home():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
    user = cursor.fetchone()
    print("DEBUG user:", user)   

    cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
    events = cursor.fetchall()
    print("DEBUG events:", events)   

    conn.close()
    return render_template("user_home.html", user=user, events=events)
    
#--------------------------------------- User Event Page ---------------------------------------------#

@app.route('/u_event')
def u_event():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    
    cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
    user = cursor.fetchone()
    print("DEBUG user:", user)   

    
    cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
    events = cursor.fetchall()
    print("DEBUG events:", events)   

    conn.close()
    return render_template("user_event.html", user=user, events=events)

#--------------------------------------- User View Event Details ---------------------------------------------#

@app.route('/view_details/<int:event_id>')
def view_details(event_id):
    if "username" in session:
        conn = get_db_connection()
        with conn.cursor() as cursor:
           
            cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
            user = cursor.fetchone()  

            
            cursor.execute("SELECT * FROM events WHERE event_id=%s", (event_id,))
            event = cursor.fetchone()
        conn.close()

        if event:
            return render_template("user_eventdetails.html", user=user, event=event)
        else:
            return "Event not found", 404
    else:
        return redirect(url_for("login"))



#--------------------------------------- User Information --------------------------------------------#

@app.route('/user_info')
def user_info():
    if "username" in session:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
            user = cursor.fetchone()
        conn.close()
        return render_template("user_information.html", user=user)
    else:
        return redirect(url_for("login"))
    
    

#--------------------------------------- User update password --------------------------------------------#

@app.route('/update_password', methods=['GET', 'POST'])
def update_password():
    if "username" not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if request.method == "POST":
        email = request.form.get("email")
        current_password = request.form.get("current_password") 
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        with conn.cursor() as cursor:
            
            cursor.execute("SELECT email, password FROM users WHERE username=%s", (session["username"],))
            result = cursor.fetchone()

            if result is None:
                flash("User not found.", "danger")
                conn.close()
                return redirect(url_for("update_password"))

            db_email = result["email"]        
            db_password = result["password"]  

            if email != db_email:
                flash("Email does not match.", "danger")
                conn.close()
                return redirect(url_for("update_password"))

            if current_password != db_password:
                flash("Incorrect current password.", "danger")
                conn.close()
                return redirect(url_for("update_password"))

            if new_password != confirm_password:
                flash("New passwords do not match.", "danger")
                conn.close()
                return redirect(url_for("update_password"))

            cursor.execute("UPDATE users SET password=%s WHERE username=%s", (new_password, session["username"]))
            conn.commit()

        conn.close()
        flash("Password updated successfully!", "success")
        return redirect(url_for("home"))
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
        user = cursor.fetchone()
    conn.close()
    return render_template("user_changepass.html", user=user)


#--------------------------------------- Upload Profile Picture --------------------------------------------#


@app.route('/upload_profile', methods=['POST'])
def upload_profile():
    if "username" not in session:
        return redirect(url_for("login"))
    
    file = request.files.get('profile_pic')
    
    if file:
        filename = file.filename 
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)  
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET profile_pic=%s WHERE username=%s",
                (filename, session["username"])
            )
            conn.commit()
        conn.close()
        flash("Profile picture updated successfully!")
    else:
        flash("No file selected.")

    return redirect(url_for("user_info"))


    
#----------------------------------------- Logout -----------------------------------------#

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)

        