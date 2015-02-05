from flask import Flask, request, redirect, url_for
import sqlite3

app = Flask(__name__)

database = 'database.db'
conn = None

def connect():
    global conn
    if conn is None:
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
    return conn

@app.teardown_appcontext
def close_conn(exception):
    global conn
    if conn is not None:
        conn.close
        conn = None

def query_db(query, args=(), one = False):
    cur = connect().cursor()
    cur.execute(query, args)
    result = cur.fetchall()
    cur.close()
    return result[0] if one else result

def add_task(task):
    query_db('insert into tasks(category, priority, description) values(?, ?, ?)', [task["category"], task["priority"], task["description"]])
    connect().commit()

def print_tasks():
    try:
        full_list = query_db("SELECT * FROM tasks")
    except sqlite3.OperationalError as e:
        print e
        print "Creating Table..."
        query_db('CREATE TABLE tasks (category VARCHAR, priority INT, description VARCHAR )')
        full_list = query_db("SELECT * FROM tasks")

    resp = ''
    resp = resp + '''
	<form method=POST action="">
		<p>Category<input type="text" name="category"></p>
		<p>Priority<input type="number" name="priority"</p>
		<p>Description<input type="text" name="description"</p>
		<p><input type=submit></p>
	</form>
    <table border = "1" cellpading="3">
		<tbody>
			<tr>
				<th>Category</th>
				<th>Priority</th>
				<th>Description</th>
			</tr>
	'''
    for task in full_list:
        c = task['category']
        p = task['priority']
        d = task['description']
        v = "%s.%s.%s" %(c, p, d)
        resp = resp + "<tr><td>%s</td><td>%s</td><td>%s</td><td><button type='submit' name='delete' value='%s'>delete</button></td></tr>" % (c, p, d, v)
    resp = resp + '</tbody></table>'
    return resp

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/task', methods=['GET', 'POST'])
def task():
    if (request.method == 'POST'):
        category = request.form['category']
        priority = request.form['priority']
        description = request.form['description']
        add_task({"category":category, "priority":priority, "description":description})
        return redirect(url_for('task'))

    return print_tasks()



if __name__ == '__main__' :
    # conn = connect()
    # c = conn.cursor()
    app.run(debug = True)
