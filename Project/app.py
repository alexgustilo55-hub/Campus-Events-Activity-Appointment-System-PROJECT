from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql

app = Flask(__name__)
app.secret_key = "12345"


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


#------------------- User Register Process ------------------#

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
        

#------------------------- Login Process --------------------------#


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
            else:
                return redirect(url_for('login'))          
        else:
            flash("Invalid username or password", "error")

    return render_template("login.html")




#--------------------------- Admin Dashboard ----------------------------#




@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template("admin_dashboard.html")





#-------------------------------------- USER HOME ----------------------------#




@app.route('/home')
def home():
    if "username" in session:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT username, email,full_name,birthday FROM users WHERE username=%s", (session["username"],))
            user = cursor.fetchone()
        conn.close()
        return render_template("home.html", user = user)
    else:
        return redirect(url_for("login"))
    



    
#----------------------------------- update --------------------------------#



@app.route('/update_profile')
def update_profile():
    return redirect(url_for("home"))



#---------------------------------- Dashboard -----------------------------#



@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template("student_dashboard.html", username=session['username'])
    else:
        return redirect(url_for('login'))
    

    
#-----------------------------------  Logout -------------------------------#



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)

        