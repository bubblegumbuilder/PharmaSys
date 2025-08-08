# I screwed up with the last backend file so I'm remaking it all over again
# This is what we will use for the whole code. flask, exclusively.
import os  # needed for loading secret key from environment
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
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
                    if role == 'admin':
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

        return render_template('AdminDashboard.html',
                               current_user=current_user,
                               user_count=user_count)
    except mysql.connector.Error as err:
        flash(f'Database error: {err}', 'error')
        return render_template('AdminDashboard.html',
                               current_user="Unknown",
                               user_count=0)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

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
@app.route('/api/inventory', methods=['POST'])
def add_drug():
    data = request.json or {}
    def to_int(v, default=0):
        try:
            return int(v)
        except (TypeError, ValueError):
            return default
    def to_dec(v, default=0.0):
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        DrugName      = (data.get('DrugName') or '').strip()
        GenericName   = (data.get('GenericName') or '').strip()
        Manufacturer  = (data.get('Manufacturer') or '').strip()
        Quantity      = to_int(data.get('Quantity'), 0)
        DosageForm    = (data.get('DosageForm') or '').strip()
        Size          = (data.get('Size') or '').strip()
        Unit          = (data.get('Unit') or '').strip()
        PurchasePrice = to_dec(data.get('PurchasePrice'), 0.0)
        SellingPrice  = to_dec(data.get('SellingPrice'), 0.0)
        ExpirationDate= (data.get('ExpirationDate') or None)  # 'YYYY-MM-DD' or None
        BatchNumber   = (data.get('BatchNumber') or '').strip()

        if not DrugName:
            return jsonify({"error":"DrugName is required"}), 400

        cursor.execute("""
            INSERT INTO drugdatabase
                (DrugName, GenericName, Manufacturer, Quantity,
                 DosageForm, Size, Unit, PurchasePrice, SellingPrice,
                 ExpirationDate, BatchNumber, LastUpdated)
            VALUES
                (%s, %s, %s, %s,
                 %s, %s, %s, %s, %s,
                 %s, %s, NOW())
        """, (DrugName, GenericName, Manufacturer, Quantity,
              DosageForm, Size, Unit, PurchasePrice, SellingPrice,
              ExpirationDate, BatchNumber))
        connection.commit()
        return jsonify({"success": True}), 201
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        try:
            cursor.close()
        except: pass
        try:
            if connection and connection.is_connected():
                connection.close()
        except: pass

@app.route('/api/inventory', methods=['DELETE'])
def delete_drug():
    ids = request.json.get('DrugIDs', [])
    if not ids:
        return jsonify({"error": "No DrugIDs provided"}), 400
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        fmt = ','.join(['%s'] * len(ids))
        cursor.execute(f"DELETE FROM drugdatabase WHERE DrugID IN ({fmt})", tuple(ids))
        deleted = cursor.rowcount
        connection.commit()
        return jsonify({"success": True, "deleted": deleted})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()

# --- GET: list inventory
@app.route('/api/inventory', methods=['GET'])
def api_inventory():
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                DrugID, Manufacturer, Quantity, DrugName, GenericName, DosageForm, Size, Unit,
                PurchasePrice, SellingPrice, ExpirationDate, BatchNumber, LastUpdated
            FROM drugdatabase
        """)
        rows = cursor.fetchall()
        for row in rows:
            if 'ExpirationDate' in row and hasattr(row['ExpirationDate'], 'isoformat'):
                row['ExpirationDate'] = row['ExpirationDate'].isoformat()
            if 'LastUpdated' in row and hasattr(row['LastUpdated'], 'isoformat'):
                row['LastUpdated'] = row['LastUpdated'].isoformat()
        return jsonify(rows)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()

# --- GET: List all accounts
@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT ID, role, Username, Password, status, FirstName, LastName
            FROM logindata
        """)
        rows = cursor.fetchall()
        return jsonify(rows)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()

# --- POST: Add a new account
@app.route('/api/accounts', methods=['POST'])
def add_account():
    data = request.json
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO logindata
                (ID, role, Username, Password, status, FirstName, LastName)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('ID'),
            data.get('role'),
            data.get('Username'),
            data.get('Password'),
            data.get('status'),
            data.get('FirstName'),
            data.get('LastName')
        ))
        connection.commit()
        return jsonify({'success': True}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()

# --- DELETE: Delete accounts by IDs
@app.route('/api/accounts', methods=['DELETE'])
def delete_accounts():
    ids = request.json.get('IDs', [])
    if not ids:
        return jsonify({'error': 'No IDs provided.'}), 400
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        # Use tuple and string formatting for variable-length IN clause
        format_strings = ','.join(['%s'] * len(ids))
        cursor.execute(f"DELETE FROM logindata WHERE ID IN ({format_strings})", tuple(ids))
        connection.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        if cursor: cursor.close()
        if connection and connection.is_connected(): connection.close()

##This is what starts flask. 
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', False)
    app.run(debug=bool(debug_mode))  # debug controlled via environment