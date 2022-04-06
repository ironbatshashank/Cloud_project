import pandas as pd
from flask import Flask, render_template, request
import mysql.connector
from mysql.connector import Error
app = Flask(__name__)

try:
    connection = mysql.connector.connect(host='35.246.79.178',
                                         database='testdb',
                                         user='cynth',
                                         password='cynth')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
except Error as e:
    print("Error while connecting to MySQL", e)



@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        name = request.form.get('name')
        address = request.form.get('Address')
        uk_city = request.form.get('UK_city')
        email = request.form.get('email')
        psw = request.form.get('psw')
        first_pref = request.form.get('University1')
        sec_pref = request.form.get('University2')
        third_pref = request.form.get('University3')
        cursor.execute('select max(id) from user_details;')
        max_id = int(list(cursor.fetchone())[0])
        ins_query = """insert into user_details (id,name,address,uk_city,email,password,first_pref,second_pref,third_pref) values values ({0},"{1}","{2}","{3}","{4}","{5}","{6}","{7}","{8}")""".format(max_id+1,name,address,uk_city,email,psw,first_pref,sec_pref,third_pref)
        print(ins_query)
        print(cursor.rowcount)
        connection.commit()
        cursor.execute('select * from user_details;')
        print(pd.DataFrame(cursor.fetchall()))
        cursor.close()
        connection.close()
    elif request.method == 'GET':
        return render_template('Signup.html')
    return render_template('Signup.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
