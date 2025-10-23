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


# Route to render the index.html page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
