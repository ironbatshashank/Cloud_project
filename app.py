import pandas as pd
from flask import Flask, render_template, request,redirect,url_for
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
        cursor.execute("select distinct email from user_details;")
        mailids = list(cursor.fetchall())
        mailids = [str(x[0]).lower() for x in mailids]
        print(mailids)
except Error as e:
    print("Error while connecting to MySQL", e)

error=None
error2=None
@app.route('/signup',methods=['GET','POST'])
@app.route('/',methods=['GET','POST'])
@app.route('/signup#',methods=['GET','POST'])
def signup(message='{}'.format(error)):
    if request.method=='POST':
        email = request.form.get('email')
        print(email)
        if email.lower().strip() in mailids:
            error = 'User already exists!!'
            print(error)
            return redirect(url_for('signup')) #render_template('signup.html',error=error)
        if email.lower().strip() not in mailids:
            name = request.form.get('name')
            address = request.form.get('Address')
            uk_city = request.form.get('UK_city')
            psw = request.form.get('psw')
            first_pref = request.form.get('University1')
            sec_pref = request.form.get('University2')
            third_pref = request.form.get('University3')
            cursor.execute('select max(id) from user_details;')
            max_id = int(list(cursor.fetchone())[0])
            ins_query = """insert into user_details (id,name,address,uk_city,email,password,first_pref,second_pref,third_pref) values ({0},"{1}","{2}","{3}","{4}","{5}","{6}","{7}","{8}")""".format(max_id+1,name,address,uk_city,email,psw,first_pref,sec_pref,third_pref)
            print(ins_query)
            # cursor.execute(ins_query)
            # print(cursor.rowcount)
            # connection.commit()
            error2 ='SignUp successful!'
            print('signup_success_error',error2)
            return redirect(url_for('signin'),code=302)
    elif request.method == 'GET':
        print('initial_signup_message',message)
        return render_template('signup.html',message='{}'.format(message))
    print('message',message)
    return render_template('signup.html',message='{}'.format(message))

@app.route('/signin',methods=['GET','POST'])
@app.route('/signin#',methods=['GET','POST'])
def signin(message2='{}'.format(error2)):
    if request.method == 'GET':
        print('initial_signin_message2',message2)
        return render_template('signin.html',message='{}'.format(message2))
    elif request.method == 'POST':
        uname = request.form.get('uname')
        print(uname)
        if uname.lower() not in mailids:
            error='User not registered.Please SignUp!'
            print('user_not_registered_error',error)
            return redirect(url_for('signup')) #render_template('signup.html',error=error2)
        elif uname.lower() in mailids:
            cursor.execute('select distinct password from user_details where email="{0}"'.format(uname))
            actual_password = str(list(cursor.fetchone())[0]).lower()
            pwd = str(request.form.get('psw')).lower()
            if actual_password==pwd:
                error2='Login successful!'
                print(error2)
                return redirect(url_for('dashboard'))
            else:
                error2='Incorrect password!'
                return redirect(url_for('signin')) #render_template('signin.html',error=error2)
    return render_template('signin.html',message='{}'.format(message2))

@app.route('/dashboard',methods=['GET','POST'])
def dashboard(message=None):
    if request.method=='GET':
        return render_template('dashboard.html',message='SignIn successful!')
if __name__ == '__main__':
    app.run()
