from flask import Flask, jsonify, render_template, request
import sqlite3
import pymongo

app = Flask(__name__)

'''
# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['book_database']  # MongoDB database
reviews_collection = db['reviews']  # MongoDB collection for reviews

# Define the path to your SQLite database file
DATABASE = 'db/books.db'
'''

#used to get all users
@app.route('/api/users', methods = ['GET'])
def get_all_users():
    try:
        return jsonify({'get_alL_users': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})

#used to get all tasks.
@app.route('/api/tasks', methods = ['GET'])
def get_all_tasks():
    try:
        return jsonify({'get_all_tasks': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})
    

@app.route('/api/task_descriptions', methods = ['GET'])
def get_all_task_descriptions():
    try:
        return jsonify({'get_all_task_descriptions': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/reflections', methods = ['GET'])
def get_all_reflections():
    try:
        return jsonify({'get_all_reflections': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/find_user', methods = ['GET'])
def find_user():
    try:
        return jsonify({'find_user': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})

#used to get all tasks.
@app.route('/api/user_tasks', methods = ['GET'])
def get_user_tasks():
    try:
        return jsonify({'get_user_task': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})
    

@app.route('/api/user_task_descriptions', methods = ['GET'])
def get_user_task_descriptions():
    try:
        return jsonify({'get_user_task_descriptions': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/user_reflections', methods = ['GET'])
def get_user_reflections():
    try:
        return jsonify({'user_reflections': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})



@app.route('/api/add_user', methods = ['Post'])
def find_user():
    try:
        return jsonify({'add_user': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})

#used to get all tasks.
@app.route('/api/add_task', methods = ['Post'])
def add_task():
    try:
        return jsonify({'add_task': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})
    

@app.route('/api/add_task_descriptions', methods = ['Post'])
def add_task_descriptions():
    try:
        return jsonify({'add_task_descriptions': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/add_reflections', methods = ['Post'])
def get_user_reflections():
    try:
        return jsonify({'add_reflections': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})
    
# Route to render the index.html page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
