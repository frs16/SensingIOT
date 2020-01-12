from flask import render_template
from app import app
from flask import render_template, request
import json 
import numpy
from sklearn.impute import SimpleImputer
import numpy as np
from datetime import time, datetime

@app.route('/')
@app.route('/index')
def index():

    return render_template('index.html', title='Home')

@app.route('/dataanalysis')
def dataanalysis():

    return render_template('dataanalysis.html', title='Dataanalysis')
    
@app.route('/prediction')
def prediction():

    return render_template('prediction.html', title='Prediction')    

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
        result = request.form
        print(result)
        now_time=datetime.strptime(result["Time"], '%H:%M')
        end_time = datetime.strptime('19:30', '%H:%M')
        start_time = datetime.strptime('07:30', '%H:%M')

        if now_time >= start_time and now_time <= end_time:
            message = "That's a busy time to travel, it would be better to travel at a different time."
        else:
            message = "That's not a busy time to travel, this is a good time to travel."

        return render_template("result.html",result = result, title = 'Results', message=message)
            
        
@app.route('/resultlight',methods = ['POST', 'GET'])
def resultlight():
   if request.method == 'POST':
        resultlight = request.form
        print(resultlight)   
        
        if resultlight['Lux'][0] == '0':
            message = "Your journey will take roughly 15 minutes."
        else:
            message = "Your journey will take roughly 19 minutes."

        return render_template("resultlight.html",result = resultlight, title = 'Results', message=message)        