from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('layout.html')

@app.route('/mongo', methods=['GET','POST'])
def mongoTest():
    client = MongoClient('mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/?retryWrites=true&w=majority')
    db = client.newDatabase
    collection = db.mongoTest
    results = collection.find()

    return render_template('mongo.html', data=results)


if __name__ == '__main__':
    app.run(debug=True)
