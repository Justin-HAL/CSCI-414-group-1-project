from flask import Flask, jsonify, render_template, request
import sqlite3
import pymongo
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['task_management_database']  # MongoDB database
task_descriptions_collection = db['task_descriptions']  # MongoDB collection for task descriptions
reflections_collection = db['reflections']  # MongoDB collection for reflections

# Define the path to your SQLite database file
DATABASE = 'db/tasks.db'

# Helper function to log errors to the database
def log_error(endpoint, error_message, error_type):
    """Log errors to the ErrorLog table in SQLite"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ErrorLog (endpoint, error_message, error_type, timestamp)
            VALUES (?, ?, ?, ?)
        """, (endpoint, error_message, error_type, datetime.now()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to log error: {str(e)}")

# ==================== USER ENDPOINTS ====================

@app.route('/api/users', methods=['GET'])
def get_all_users():
    """Get all users from the database"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, first_name, last_name, email FROM Users")
        users = cursor.fetchall()
        conn.close()

        user_list = []
        for user in users:
            user_dict = {
                'user_id': user[0],
                'first_name': user[1],
                'last_name': user[2],
                'email': user[3]
            }
            user_list.append(user_dict)

        return jsonify({'users': user_list})
    except Exception as e:
        log_error('/api/users', str(e), 'Database Error')
        return jsonify({'error': str(e)}), 500

@app.route('/api/find_user', methods=['GET'])
def find_user():
    """Find a user by email or user_id"""
    try:
        email = request.args.get('email')
        user_id = request.args.get('user_id')
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        if email:
            cursor.execute("SELECT user_id, first_name, last_name, email FROM Users WHERE email = ?", (email,))
        elif user_id:
            cursor.execute("SELECT user_id, first_name, last_name, email FROM Users WHERE user_id = ?", (user_id,))
        else:
            conn.close()
            return jsonify({'error': 'Please provide email or user_id parameter'}), 400
        
        user = cursor.fetchone()
        conn.close()

        if user:
            user_dict = {
                'user_id': user[0],
                'first_name': user[1],
                'last_name': user[2],
                'email': user[3]
            }
            return jsonify({'user': user_dict})
        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        log_error('/api/find_user', str(e), 'Database Error')
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_user', methods=['POST'])
def add_user():
    """Add a new user to the database"""
    try:
        data = request.get_json()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')

        if not all([first_name, last_name, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT user_id FROM Users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'User with this email already exists'}), 409

        cursor.execute("""
            INSERT INTO Users (first_name, last_name, email, password)
            VALUES (?, ?, ?, ?)
        """, (first_name, last_name, email, password))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({'message': 'User added successfully', 'user_id': user_id}), 201

    except Exception as e:
        log_error('/api/add_user', str(e), 'Database Error')
        return jsonify({'error': str(e)}), 500

# ==================== TASK ENDPOINTS (SQL) ====================

@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    """Get all tasks from the database"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.task_id, t.user_id, t.rank, t.status, t.due_date,
                   u.first_name, u.last_name, u.email
            FROM Tasks t
            LEFT JOIN Users u ON t.user_id = u.user_id
        """)
        tasks = cursor.fetchall()
        conn.close()

        task_list = []
        for task in tasks:
            task_dict = {
                'task_id': task[0],
                'user_id': task[1],
                'rank': task[2],
                'status': task[3],
                'due_date': task[4],
                'user': {
                    'first_name': task[5],
                    'last_name': task[6],
                    'email': task[7]
                }
            }
            task_list.append(task_dict)

        return jsonify({'tasks': task_list})
    except Exception as e:
        log_error('/api/tasks', str(e), 'Database Error')
        return jsonify({'error': str(e)}), 500

@app.route('/api/user_tasks', methods=['GET'])
def get_user_tasks():
    """Get all tasks for a specific user"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Please provide user_id parameter'}), 400

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT task_id, user_id, rank, status, due_date
            FROM Tasks
            WHERE user_id = ?
            ORDER BY rank ASC, due_date ASC
        """, (user_id,))
        tasks = cursor.fetchall()
        conn.close()

        task_list = []
        for task in tasks:
            task_dict = {
                'task_id': task[0],
                'user_id': task[1],
                'rank': task[2],
                'status': task[3],
                'due_date': task[4]
            }
            task_list.append(task_dict)

        return jsonify({'tasks': task_list})
    except Exception as e:
        log_error('/api/user_tasks', str(e), 'Database Error')
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_task', methods=['POST'])
def add_task():
    """Add a new task to the database"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        rank = data.get('rank')
        status = data.get('status', 'not complete')
        due_date = data.get('due_date')

        if not all([user_id, rank, due_date]):
            return jsonify({'error': 'Missing required fields (user_id, rank, due_date)'}), 400

        # Validate rank
        if rank not in [1, 2, 3, 4]:
            return jsonify({'error': 'Rank must be 1, 2, 3, or 4'}), 400

        # Validate status
        if status not in ['not complete', 'completed', 'missed']:
            return jsonify({'error': 'Status must be: not complete, completed, or missed'}), 400

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Verify user exists
        cursor.execute("SELECT user_id FROM Users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'User not found'}), 404

        cursor.execute("""
            INSERT INTO Tasks (user_id, rank, status, due_date)
            VALUES (?, ?, ?, ?)
        """, (user_id, rank, status, due_date))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({'message': 'Task added successfully', 'task_id': task_id}), 201

    except Exception as e:
        log_error('/api/add_task', str(e), 'Database Error')
        return jsonify({'error': str(e)}), 500

# ==================== TASK DESCRIPTION ENDPOINTS (MongoDB) ====================

@app.route('/api/task_descriptions', methods=['GET'])
def get_all_task_descriptions():
    """Get all task descriptions from MongoDB"""
    try:
        task_descriptions = list(task_descriptions_collection.find({}, {'_id': 0}))
        return jsonify({'task_descriptions': task_descriptions})
    except Exception as e:
        log_error('/api/task_descriptions', str(e), 'MongoDB Error')
        return jsonify({'error': str(e)}), 500

@app.route('/api/user_task_descriptions', methods=['GET'])
def get_user_task_descriptions():
    """Get task descriptions for a specific user's tasks"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Please provide user_id parameter'}), 400

        # First, get all task_ids for this user from SQL
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT task_id FROM Tasks WHERE user_id = ?", (int(user_id),))
        task_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        # Then get task descriptions for those task_ids from MongoDB
        task_descriptions = list(task_descriptions_collection.find(
            {'task_id': {'$in': task_ids}}, 
            {'_id': 0}
        ))

        return jsonify({'task_descriptions': task_descriptions})
    except Exception as e:
        log_error('/api/user_task_descriptions', str(e), 'Database Error')
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_task_description', methods=['POST'])
def add_task_description():
    """Add a new task description to MongoDB"""
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        title = data.get('title')
        description = data.get('description', '')
        steps = data.get('steps', [])

        if not all([task_id, title]):
            return jsonify({'error': 'Missing required fields (task_id, title)'}), 400

        # Verify task exists in SQL database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT task_id FROM Tasks WHERE task_id = ?", (task_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Task not found'}), 404
        conn.close()

        # Check if task description already exists
        existing = task_descriptions_collection.find_one({'task_id': task_id})
        if existing:
            return jsonify({'error': 'Task description already exists for this task'}), 409

        # Insert task description into MongoDB
        task_description = {
            'task_id': task_id,
            'title': title,
            'description': description,
            'steps': steps
        }
        result = task_descriptions_collection.insert_one(task_description)

        return jsonify({
            'message': 'Task description added successfully',
            'task_id': task_id
        }), 201

    except Exception as e:
        log_error('/api/add_task_description', str(e), 'MongoDB Error')
        return jsonify({'error': str(e)}), 500

# ==================== REFLECTION ENDPOINTS (MongoDB) ====================

@app.route('/api/reflections', methods=['GET'])
def get_all_reflections():
    """Get all reflections from MongoDB"""
    try:
        reflections = list(reflections_collection.find({}, {'_id': 0}))
        return jsonify({'reflections': reflections})
    except Exception as e:
        log_error('/api/reflections', str(e), 'MongoDB Error')
        return jsonify({'error': str(e)}), 500

@app.route('/api/user_reflections', methods=['GET'])
def get_user_reflections():
    """Get reflections for a specific user's tasks"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Please provide user_id parameter'}), 400

        # First, get all task_ids for this user from SQL
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT task_id FROM Tasks WHERE user_id = ?", (int(user_id),))
        task_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        # Then get reflections for those task_ids from MongoDB
        reflections = list(reflections_collection.find(
            {'task_id': {'$in': task_ids}}, 
            {'_id': 0}
        ))

        return jsonify({'reflections': reflections})
    except Exception as e:
        log_error('/api/user_reflections', str(e), 'Database Error')
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_reflection', methods=['POST'])
def add_reflection():
    """Add a new reflection to MongoDB"""
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        reflection_type = data.get('reflection_type', 'missed_task')
        content = data.get('content', {})

        if not task_id:
            return jsonify({'error': 'Missing required field: task_id'}), 400

        # Verify task exists in SQL database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT task_id, status FROM Tasks WHERE task_id = ?", (task_id,))
        task = cursor.fetchone()
        if not task:
            conn.close()
            return jsonify({'error': 'Task not found'}), 404
        conn.close()

        # Insert reflection into MongoDB
        reflection = {
            'task_id': task_id,
            'reflection_date': datetime.now().isoformat(),
            'reflection_type': reflection_type,
            'content': {
                'reason': content.get('reason', ''),
                'emotions': content.get('emotions', []),
                'lessons_learned': content.get('lessons_learned', ''),
                'action_items': content.get('action_items', [])
            }
        }
        result = reflections_collection.insert_one(reflection)

        return jsonify({
            'message': 'Reflection added successfully',
            'task_id': task_id
        }), 201

    except Exception as e:
        log_error('/api/add_reflection', str(e), 'MongoDB Error')
        return jsonify({'error': str(e)}), 500

# ==================== ERROR LOG ENDPOINTS ====================

@app.route('/api/error_logs', methods=['GET'])
def get_error_logs():
    """Get all error logs from the database"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT log_id, endpoint, error_message, error_type, timestamp
            FROM ErrorLog
            ORDER BY timestamp DESC
        """)
        logs = cursor.fetchall()
        conn.close()

        log_list = []
        for log in logs:
            log_dict = {
                'log_id': log[0],
                'endpoint': log[1],
                'error_message': log[2],
                'error_type': log[3],
                'timestamp': log[4]
            }
            log_list.append(log_dict)

        return jsonify({'error_logs': log_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== HOME ROUTE ====================

@app.route('/')
def index():
    """Render the main index page"""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")