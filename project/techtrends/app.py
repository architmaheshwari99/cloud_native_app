import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging

# Function to get a database connection.
# This function connects to database with the name `database.db`
connection_count = 0

def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global connection_count
    connection_count+=1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    from datetime import datetime
    current_time = datetime.now().time()

    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()


    app.logger.info(' '.join([str(current_time), post['title'], 'retrieved']))

    global connection_count
    connection_count-=1
    connection.close()

    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    global connection_count
    connection_count-=1
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the Health page
@app.route('/healthz')
def healthz():
    response_data = {
        'result': 'OK - healthy'
    }
    return jsonify(response_data), 200

# Define the Metric page
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('SELECT count(*) FROM posts').fetchone()[0]
    global connection_count
    connection_count-=1
    connection.close()

    response_data = {
        'result': post_count,
        'db_connection_count': connection_count
    }
    return jsonify(response_data), 200

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    global connection_count

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection_count-=1
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(filename='app.log',level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')

