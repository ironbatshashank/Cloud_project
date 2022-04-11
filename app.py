import pandas as pd
from flask import Flask, render_template, request,redirect,url_for,flash,session
import mysql.connector
from requests import get
from mysql.connector import Error
from passlib.hash import pbkdf2_sha256
app = Flask(__name__)
app.secret_key='1234'

uni_dict = {'Queen Mary University of London':'London',
            'London School of Economics':'London',
            'Kings college London':'London',
            'Imperial College London':'London',
            'Oxford University':'Oxford',
            'University of Edinburgh':'Edinburgh',
            'University of Manchester':'Manchester',
            'University of Warwick':'Warwick',
            'University of Glasgow':'Glasgow',
            'University of Cambridge':'Cambridge'}

url = '''https://www.reed.co.uk/api/1.0/search?keywords={keywords}&locationName={locationName}&distanceFromLocation={distance}'''

try:
    connection = mysql.connector.connect(host='34.105.148.167',
                                         database='testdb',
                                         user='cloud',
                                         password='cloud')
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

signup_message = None

@app.route('/signup',methods=['GET','POST'])
@app.route('/',methods=['GET','POST'])
def signup(signup_message=signup_message):

    session.clear()
    if request.method=='POST':
        session.pop('email', None)
        email = request.form.get('email')
        cursor.execute("select distinct email from user_details;")
        mailids = list(cursor.fetchall())
        mailids = [str(x[0]).lower() for x in mailids]
        if email.lower().strip() in mailids:
            flash('User already exists!!')
            signup_message='User already exists!!'
            return redirect(url_for('signup')) #render_template('signup.html',error=error)
        if email.lower().strip() not in mailids:
            name = request.form.get('name')
            address = request.form.get('Address')
            uk_city = request.form.get('UK_city')
            psw = pbkdf2_sha256.encrypt(request.form.get('psw'))
            print(psw)
            # psw = request.form.get('psw')
            first_pref = request.form.get('University1')
            sec_pref = request.form.get('University2')
            third_pref = request.form.get('University3')
            cursor.execute('select max(id) from user_details;')
            max_id = int(list(cursor.fetchone())[0])
            ins_query = """insert into user_details (id,name,address,uk_city,email,password,first_pref,second_pref,third_pref) values ({0},"{1}","{2}","{3}","{4}","{5}","{6}","{7}","{8}")""".format(max_id+1,name,address,uk_city,email,psw,first_pref,sec_pref,third_pref)
            # print(ins_query)
            cursor.execute(ins_query)
            print(cursor.rowcount)
            connection.commit()
            flash('SignUp successful!')
            return redirect(url_for('signin'))
    elif request.method == 'GET':
        return render_template('signup.html')
    return render_template('signup.html')

@app.route('/signin',methods=['GET','POST'])
def signin():
    session.clear()
    if request.method == 'GET':
        return render_template('signin.html')
    elif request.method == 'POST':
        uname = request.form.get('uname')
        print(uname)
        cursor.execute("select distinct email from user_details;")
        mailids = list(cursor.fetchall())
        mailids = [str(x[0]).lower() for x in mailids]
        if uname.lower() not in mailids:
            flash('User not registered.Please SignUp!')
            return redirect(url_for('signup')) #render_template('signup.html',error=error2)
        elif uname.lower() in mailids:
            cursor.execute('select distinct password from user_details where email="{0}"'.format(uname))
            actual_password = list(cursor.fetchone())[0]
            pwd = str(request.form.get('psw')).lower()
            if pbkdf2_sha256.verify(request.form.get('psw'),actual_password):
                flash('Login successful!')
                session['email'] = uname
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect password!')
                return redirect(url_for('signin'))
    return render_template('signin.html')

@app.route('/dashboard',methods=['GET','POST'])
def dashboard(session=session):
    if request.method=='GET':
        if session:
            uname = session['email']
            print(uname)
            cursor.execute("select name,address,uk_city,email,first_pref,second_pref,third_pref from user_details where email='{}';".format(uname))
            (name,address,uk_city,email,first_pref,second_pref,third_pref) = cursor.fetchall()[0]
            print(cursor.fetchall())
            jobs = pd.DataFrame(columns=['Employer','Title','Location','Salary','URL'])
            accoms = pd.DataFrame(columns=['Around University','Description','Distance from Uni','Rent','URL'])
            for uni in [first_pref,second_pref,third_pref]:
                response = get(url.format(keywords='part time', locationName=uni_dict[uni], distance=5),
                               auth=('ed373226-6530-4b21-9c08-5675064596ca', ''))
                jobs_list = []
                for r in response.json()['results']:
                    jobs_list.append((r['employerName'], r['jobTitle'], r['locationName'], r['minimumSalary'], r['jobUrl']))
                jobs = pd.concat([jobs,pd.DataFrame(jobs_list, columns=['Employer', 'Title', 'Location', 'Salary', 'URL']).head(5)],axis=0,ignore_index=True)

                cursor.execute("select * from rent where university_name='{}' LIMIT 5;".format(uni))
                accoms = pd.concat([accoms,pd.DataFrame(list(cursor.fetchall()),columns=['Around University','Description','Distance from Uni','Rent','URL'])],axis=0,ignore_index=True)

            return render_template('dashboard.html',Name=name,Address=address,UK_city=uk_city,
                                   Email=email,first_pref=first_pref,sec_pref=second_pref,third_pref=third_pref,
                                   rents=[accoms.to_html(classes='data',header=True,index=False)]
                                   ,jobs=[jobs.to_html(classes='data',header=True,index=False)])
        else:
            return redirect(url_for('signin'))
    if request.method == 'POST':
        uname = session['email']
        print(request.form.get('address_update'))
        print(request.form.get('logout'))
        print(request.form.get('delete'))
        if request.form.get('address_update'):
            new_address = request.form.get('address_update')
            print(new_address)
            update_query = "Update user_details set address='{new_address}' where email='{email}';".format(new_address=new_address,email=uname)
            print(update_query)
            cursor.execute(update_query)
            print(cursor.fetchall())
            connection.commit()
            return redirect(url_for('dashboard'))
        if request.form.get('logout')=='Logout':
            print('logged out')
            session.pop('email')
            session.clear()
            #session['email']=None
            return redirect(url_for('signin'))
        if request.form.get('delete') == 'Delete My Data':
            uname=session['email']
            cursor.execute("delete from user_details where email='{}';".format(uname))
            connection.commit()
            session.pop('email')
            session.clear()
            return redirect(url_for('signin'))
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
