# I screwed up with the last backend file so I'm remaking it all over again
# This is what we will use for the whole code. flask, exclusively.
import os  # needed for loading secret key from environment
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash  # for secure password handling
# MySQL connector for backend integration
import mysql.connector

# This line is needed to initialize flask
app = Flask(__name__,
            static_url_path='/static',
            static_folder='static',
            template_folder='templates')

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_very_secret_key_for_session_management')  # Required for flash messages; load from env

# MySQL database config block
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'pharmasys',
    'port': 3307 #temporary for server target using xampp
}


##LOG IN SECTION-----------------------------------------------------------------------------------------------
##the back slash is an appending prefix with the GET method implying a request from the html
##note: GET is used to jump from HTML to HTML if action is detected
@app.route('/', methods=['GET'])
##no idea why its called index but hey
def index():
    # Renders the initial form page, which in this case, is Login.html
    return render_template('Login.html')

##depending on what the action states, this is returned and simulated.
##note: POST is used to simulate actions depending on what is requested on the HTML. e.g. if a button on the form says submit form, then grab that form and init
@app.route('/login', methods=['POST'])
def submit_form():
    # Handles form submission and performs validation.
    if request.method == 'POST':
        employeeId = request.form.get('employeeId')
        username = request.form.get('username')
        password = request.form.get('password')

        errors = []


        # Server-side validation logic
        if not employeeId:
            errors.append("employeeId is required.")
        elif len(employeeId) > 8:
            errors.append("Invalid employeeId.")

        if not username:
            errors.append("Username is required.")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters long.")

        if not password:
            errors.append("Password is required.")
        elif len(password) < 3:
            errors.append("Password must be at least 3 characters long.")

        if errors:
            # If validation fails, re-render the form with error messages
            for error in errors:
                flash(error, 'error')  # 'error' is a category for styling
            return render_template('Login.html',
                                   username=username,
                                   employeeId=employeeId)  # Pass back submitted data to pre-fill form
        else:
            connection = None
            cursor = None
            try:
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor(dictionary=True)  # fetch results as a dict instead of tuple
                # Verify credentials instead of inserting
                cursor.execute(
                    "SELECT ID, Password, role FROM LoginData WHERE ID=%s AND Username=%s",
                    (employeeId, username)
                )
                user = cursor.fetchone()
                if user and user['Password'] == password:
                    #console brute force testing
                    print("Input password:", password)
                    role = user.get('role', '').lower()
                    flash('Login successful!', 'success')
                    if role == 'Admin':
                        print("Admin Detected")
                        session['username'] = username
                        return redirect(url_for('admin_dashboard'))
                    elif role == 'user':
                        print("User Detected")
                        session['username'] = username
                        return redirect(url_for('dashboard_page'))
                    else:
                        print("who u")
                        flash('Unknown role. Access denied.', 'error')
                        return render_template('Login.html')
                else:
                    print("No account or invalid creds")
                    flash('Invalid credentials.', 'error')
                    return render_template('Login.html')
            except mysql.connector.Error as err:
                flash(f'Database error: {err}', 'error')
                return render_template('Login.html')
            finally:
                if cursor:
                    cursor.close()
                if connection and connection.is_connected():
                    connection.close()
    return redirect(url_for('index'))  # Redirect if accessed via GET

@app.route('/login_success')
def login_success_page():
    # Renders a success page after successful Login form submission.
    return render_template('LoginSuccess.html')

@app.route('/success')
def success_page():
    # Renders a success page after successful Signup form submission.
    return render_template('success.html')

@app.route('/dashboard', methods=['GET'])
def dashboard_page():
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # TEMPORARY: Use hardcoded username as current_user
        current_user = session['username']

        # Get number of users
        cursor.execute("SELECT COUNT(*) AS total FROM LoginData")
        result = cursor.fetchone()
        user_count = result['total'] if result else 0

        return render_template('UserDashboard.html',
                               current_user=current_user,
                               user_count=user_count)
    except mysql.connector.Error as err:
        flash(f'Database error: {err}', 'error')
        return render_template('UserDashboard.html',
                               current_user="Unknown",
                               user_count=0)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
    return render_template('AdminDashboard.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET'])
def signup_page():
    # Renders the signup form page, which in this case, is SignUp.html
    return render_template('SignUp.html')

# This is where the signup will check
@app.route('/signup', methods=['POST'])
def submit_signup():
    if request.method == 'POST':
        # These are variables to be retrieved from the signup page
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        employeeId = request.form.get('employeeId')
        username = request.form.get('username')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirmPassword')

        errors = []

        # We want to check if any values are empty
        if not firstName:
            errors.append("First name is required.")
        if not lastName:
            errors.append("Last name is required.")
        if not employeeId:
            errors.append("Employee ID is required.")
        elif len(employeeId) > 8:
            errors.append("Invalid Employee ID.")
        if not username:
            errors.append("Username is required.")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters long.")
        if not password:
            errors.append("Password is required.")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if not confirmPassword:
            errors.append("Please confirm your password.")
        elif password != confirmPassword:
            errors.append("Passwords do not match.")

        # Check if any errors exist and flash them
        if errors:
            for error in errors:
                flash(error, 'error')
            print("Validation errors (signup):", errors)
            return render_template('SignUp.html',
                                   firstName=firstName,
                                   lastName=lastName,
                                   username=username,
                                   employeeId=employeeId)
        else:
            connection = None
            cursor = None
            try:
                # print in console for debugging purposes. This let's us verify if task is thrown at the plugging process of form to csv
                print("Inserting new user:", employeeId, username)
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor()
                #disabled password hashing temporarily for prototyping [IMPORTANT BTW]
                    ### hash password before storing
                    ##hashed_password = generate_password_hash(password)
                # Insert the account into the users database
                cursor.execute(
                    "INSERT INTO LoginData (ID, role, Username, Password, status, FirstName, LastName) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (employeeId, 'user', username, password, 'active', firstName, lastName)
                )
                connection.commit()
                flash('Account created successfully!', 'success')
                print("Signup successful. Redirecting to success page.")
                return redirect(url_for('success_page'))
            except mysql.connector.Error as err:
                flash(f'Database error: {err}', 'error')
                print("MySQL error (signup):", err)
                return render_template('SignUp.html')
            finally:
                if cursor:
                    cursor.close()
                if connection and connection.is_connected():
                    connection.close()
    return redirect(url_for('signup_page'))


##This is what starts flask. 
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', False)
    app.run(debug=bool(debug_mode))  # debug controlled via environment
