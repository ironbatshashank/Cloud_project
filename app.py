from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        st_name = request.form.get('name')
        st_address = request.form.get('Address')

    elif request.method == 'GET':
        return render_template('Signup.html')
    print(st_name)
    print(st_address)
    return render_template('Signup.html')




if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
