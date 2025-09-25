from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql,os

app = Flask(__name__)
app.secret_key = "12345"
app.config['UPLOAD_FOLDER'] = "static/img_profile/"


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
       
       role = request.form['role']
       gender = request.form['gender']
       id = request.form['id']
       fullname = request.form['fullname']
       phone = request.form['phone']
       birthday = request.form['birthday']
       email = request.form['email']
       address = request.form['address']
       username = request.form['username']
       password = request.form['password']

       
       conn = get_db_connection()
       cursor = conn.cursor()
       cursor.execute("INSERT INTO users (role,gender,id,full_name,phone,birthday, email, address, username, password) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (role,gender,id,fullname,phone,birthday, email, address, username, password))
       conn.commit()
       conn.close()
       
       flash("Registration successful!")
       return redirect(url_for('login'))
   
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
            elif user['role'] == 'user':
                return redirect(url_for('home'))
            elif user['role'] == 'student':
                return redirect(url_for('home'))
            elif user['role'] == 'faculty':
                return redirect(url_for('home'))
            elif user['role'] == 'staff':
                return redirect(url_for('home'))
            else:
                return redirect(url_for('login'))          
        else:
            flash("Invalid username or password", "error")

    return render_template("login.html")


#------------------------------------- Admin Dashboard -----------------------------------#


@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template("admin_dashboard.html")

#-------------------------------------- User home page ------------------------------#

@app.route('/home')
def home():

    if "username" in session:
        if "username" in session:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
                user = cursor.fetchone()  
        conn.close()
        return render_template("home.html", user=user)  
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
    
    

#--------------------------------------- update password --------------------------------------------#

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


#--------------------------------------- Upload Profile Piture --------------------------------------------#


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

        