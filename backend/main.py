from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
app = Flask(__name__)
app.secret_key = "superhardpw"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)

class Machine(db.Model):
    __tablename__ = 'Machine'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)

class Stock(db.Model):
    __tablename__ = 'Stock'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('Machine.id'), nullable=False)
    product = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def run():
    return 'Running properly'

@app.route('/addMachine/', methods=['POST'])
def addMachine():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        newMachine = Machine(name=json["name"], location=json["location"])
        db.session.add(newMachine)
        db.session.commit()
        return json

@app.route('/addStock/', methods=['POST'])
def addStock():
    try:
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            json = request.json
            newStock = Stock(product=json["product"], amount=json["amount"], machine_id=json["machine_id"])
            db.session.add(newStock)
            db.session.commit()
            return json
    except:
        return {'failed': "unkown machine_id"}

@app.route('/deleteMachine/', methods=['DELETE'])
def removeMachine():
    try:
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            json = request.json
            Stock.query.filter_by(machine_id=json["id"]).delete()
            Machine.query.filter_by(id=json["id"]).delete()
            db.session.commit()
            return json
    except:
        return {'failed': "unkown machine_id "}

@app.route('/deleteStock/', methods=['DELETE'])
def removeStock():
    try:
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            json = request.json
            Stock.query.filter_by(id=json["id"]).delete()
            db.session.commit()
            return json
    except:
        return {'failed': "unkown stock_id"}

@app.route('/machineStock/', methods=['GET'])
def machineStock():
    try:
        conteny_type = request.headers.get('Content-Type')
        if (conteny_type == 'application/json'):
            id = request.json["id"]
            stock = Stock.query.filter_by(machine_id=id).all()
            machineStock = [{'id': s.id, 'machine_id': s.machine_id, 'product': s.product, 'amount': s.amount} for s in
                                stock]
            return jsonify(machineStock)
    except:
        return {'failed': "unknown machine_id"}

@app.route('/editMachine/', methods=['PUT'])
def editMachine():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        updateMachine = Machine.query.filter_by(id=json["id"]).first()
        updateMachine.name = json["name"]
        updateMachine.location = json["location"]
        db.session.commit()
        return json

@app.route('/editStock/', methods=['PUT'])
def editStock():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        updateStock = Stock.query.filter_by(id=json["id"]).first()
        updateStock.product = json["product"]
        updateStock.machine_id = json["machine_id"]
        updateStock.amount = json["amount"]
        db.session.commit()
        return json

@app.route('/allMachines/', methods=['GET'])
def allMachines():
    machines = Machine.query.all()
    machinesLst = [{'id': machine.id, 'name': machine.name, 'location': machine.location} for machine in machines]
    return jsonify(machinesLst)

@app.route('/allStocks/', methods=['GET'])
def allStocks():
    stocks = Stock.query.all()
    stocksLst = [{'id': stock.id, 'machine_id': stock.machine_id, 'product': stock.product, 'amount': stock.amount} for stock in stocks]
    return jsonify(stocksLst)

if __name__ == '__main__':
    app.run()