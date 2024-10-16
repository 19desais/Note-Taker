# Import necessary modules from Flask and SQLite3
from flask import Flask, render_template, request, redirect, url_for, g, flash
import sqlite3

# Create an instance of the Flask application
app = Flask(__name__)

# Secret key used for flash messaging
app.secret_key = 'your_secret_key'

# Path to the SQLite database file
DATABASE = 'notes.db'

# Function to connect to the SQLite database
def get_db():
    # Check if a database connection exists for the request 
    db = getattr(g, '_database', None)
    if db is None:
        # If not, create a new connection
        db = g._database = sqlite3.connect(DATABASE)
    return db                                                                                                                                                                                                               

# Close the database connection when the request is torn down
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()  # Close the connection if it exists

# Route for the homepage with GET and POST methods
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Extract email from the form and save it in the 'users' table
        email = request.form['email']
        conn = get_db()  # Get database connection
        c = conn.cursor()  # Create a cursor
        c.execute('INSERT INTO users (email) VALUES (?)', (email,))  # Insert email
        conn.commit()  # Commit the transaction
        conn.close()  # Close the connection
        return redirect(url_for('note'))  # Redirect to the 'note' page
    return render_template('Notetaker.html')  # Render the home page 

# Route for the note-taking page with GET and POST methods
@app.route('/note', methods=['GET', 'POST'])
def note():
    conn = get_db()  # Get database connection
    c = conn.cursor()  # Create a cursor
    
    if request.method == 'POST':
        # Save the submitted note into the 'notes' table
        note = request.form['note']
        c.execute('INSERT INTO notes (note) VALUES (?)', (note,))
        conn.commit()  # Commit the transaction

    # Fetch all notes from the 'notes' table to display on the page
    c.execute('SELECT note FROM notes')
    notes = c.fetchall()  # Retrieve all notes
    
    conn.close()  # Close the connection
    return render_template('notetaker.html', notes=notes)  # Render the note-taking page with the list of notes

# Route to delete the last note entered
@app.route('/delete', methods=['POST'])
def delete():
    conn = get_db()  # Get database connection
    c = conn.cursor()  # Create a cursor
    c.execute('SELECT rowid FROM notes ORDER BY rowid DESC LIMIT 1')  # Get the rowid of the last note
    last_note = c.fetchone()  # Fetch the last note
    if last_note:
        c.execute('DELETE FROM notes WHERE rowid = ?', (last_note[0],))  # Delete the last note
        conn.commit()  # Commit the transaction
    conn.close()  # Close the connection
    return redirect(url_for('note'))  # Redirect to the 'note' page

# Route for a login functionality with a password check
@app.route('/log', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        # Check the password from the form submission
        password = request.form['password']
        if password == 'Password123':  # The Admin Password
            conn = get_db()  # Get database connection
            c = conn.cursor()  # Create a cursor
            c.execute('SELECT email FROM users')  # Fetch all user emails
            emails = c.fetchall()  # Retrieve all emails
            conn.close()  # Close the connection
            return render_template('log.html', emails=emails)  # Render the log page with the emails
        else:
            flash('Incorrect password. Please try again.')  # Flash an error message if password is wrong
    return render_template('password.html')  # Render the  Admin password page

# Route to go back to the homepage
@app.route('/go_back', methods=['POST'])
def go_back():
    return redirect(url_for('home'))  # Redirect to the 'home' route

# Main entry point of the application
if __name__ == '__main__':
    # Run the Flask development server on localhost with debugging enabled
    app.run(host='127.0.0.1', port=8080, debug=True)
