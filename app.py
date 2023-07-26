from flask import Flask, flash, render_template, request, redirect, session, url_for
from flask_session import Session
from sqlite3 import connect
from livereload import Server
import requests

app = Flask(__name__)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

db = connect('foodshop.db', check_same_thread=False)

    
    

def send_line(token, msg):
    url = 'https://notify-api.line.me/api/notify'
    token = token
    headers = {'content-type': 'application/x-www-form-urlencoded',
               'Authorization': 'Bearer '+token}
    msg = msg
    r = requests.post(url, headers=headers, data={'message': msg})


@app.route('/line', methods=['GET', 'POST'])
def line():
    
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # get post data name 'line' from form
        line = request.form.get('line')

        # check line token on user_id from database if exist then update else insert
        rows = db.execute(
            'SELECT id FROM line_token WHERE user_id=?', (session['user_id'],))
        line_id = rows.fetchone()
        if line_id:
            db.execute('UPDATE line_token SET token=? WHERE user_id=?',
                       (line, session['user_id']))
        else:
            db.execute('INSERT INTO line_token (token, user_id) VALUES (?,?)',
                       (line, session['user_id']))

        # commit to database
        db.commit()

        name = session['name']

        # test send line 3 line message
        send_line(line, f'\nHello {name},\nThis is test from foodshop')

        # return to success page with message success
        return render_template('success.html', message='success')

    else:
        return redirect(url_for('setting'))


@app.route('/settable', methods=['GET', 'POST'])
def settable():

    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        table = request.form.get('table')
        
        if table == '':
            table = 0
        
        # check table on user_id from database if exist then update else insert
        rows = db.execute(
            'SELECT id FROM shop_table WHERE user_id=?', (session['user_id'],))
        table_id = rows.fetchone()
        if table_id:
            db.execute('UPDATE shop_table SET quantity=? WHERE user_id=?',
                       (table, session['user_id']))
        else:
            db.execute('INSERT INTO shop_table (quantity, user_id) VALUES (?,?)',
                       (table, session['user_id']))

        # commit to database
        db.commit()

        # return to success page with message success
        return redirect(url_for('setting'))

    else:
        return redirect(url_for('setting'))


@app.route('/status_order', methods=['GET', 'POST'])
def status_order():
    
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        id = request.form.get('id')
        table = request.form.get('table')
        
        db.execute('UPDATE orders SET status=? WHERE id=?', (2, id))
        
        db.commit()
        
        return redirect(url_for('menu', table=table))

    else:
        return redirect(url_for('index'))


@app.route('/delete_order', methods=['GET', 'POST'])
def delete_order():
    
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        id = request.form.get('id')
        table = request.form.get('table')
        
        db.execute('DELETE FROM orders WHERE id=?', (id,))
        
        db.commit()
        
        return redirect(url_for('menu', table=table))

    else:
        return redirect(url_for('index'))
        

@app.route('/addmenu', methods=['GET', 'POST'])
def addmenu():
    
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')

        # check menu on user_id from items database if exist then update else insert
        rows = db.execute(
            'SELECT id FROM items WHERE user_id=? AND name=?', (session['user_id'], name))
        item_id = rows.fetchone()
        if item_id:
            db.execute('UPDATE items SET price=? WHERE user_id=? AND name=?',
                       (price, session['user_id'], name))
        else:
            db.execute('INSERT INTO items (name, price, user_id, status) VALUES (?,?,?,?)',
                       (name, price, session['user_id'], 1))

        # commit to database
        db.commit()

        # return to success page with message success
        return redirect(url_for('setting'))

    else:
        return redirect(url_for('setting'))


@app.route('/menustatus', methods=['GET', 'POST'])
def menustatus():
    
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        id = request.form.get('id')
        status = request.form.get('status')
        
        if status == '1':
            db.execute('UPDATE items SET status=? WHERE id=?', (1, id))
        else:
            db.execute('UPDATE items SET status=? WHERE id=?', (0, id))
        
        db.commit()
        
        # return to success page with message success
        return redirect(url_for('setting'))

    else:
        return redirect(url_for('setting'))


@app.route('/deletemenu', methods=['GET', 'POST'])
def deletemenu():
    
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        id = request.form.get('id')
        
        db.execute('DELETE FROM items WHERE id=?', (id,))
        db.commit()
        
        # return to success page with message success
        return redirect(url_for('setting'))

    else:
        return redirect(url_for('setting'))
    
    
@app.route('/order', methods=['GET', 'POST'])
def order():
    
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        table = request.form.get('table')
        item_id = request.form.get('menu')
        quantity = request.form.get('quantity')
        comment = request.form.get('comment')
        
                
        # insert order to database
        db.execute('INSERT INTO orders (user_id,item_id,quantity,table_name,status,comment) VALUES (?,?,?,?,?,?)', (session['user_id'],item_id,quantity,table,1,comment))
        
        # commit to database
        db.commit()
        
        # line token from database
        rows = db.execute('SELECT token FROM line_token WHERE user_id=?', (session['user_id'],))
        line = rows.fetchone()
        line = line[0]
        
        
        # item_id to name from database
        rows = db.execute('SELECT name FROM items WHERE id=?', (item_id,))
        name = rows.fetchone()
        name = name[0]
        
        send_line(line, f'\nOrder from table {table}\n ---- \n Menu : {name} \n Quantity : {quantity}\n Comment : {comment}')
        
        return redirect(url_for('menu', table=table))
    
        

@app.route('/bill', methods=['GET', 'POST'])
def bill():
    
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        table = request.form.get('table')
        
        # orders from database
        rows = db.execute('SELECT orders.id,items.name,items.price,orders.quantity,orders.comment,orders.status FROM orders INNER JOIN items ON orders.item_id=items.id WHERE orders.user_id=? AND table_name=?', (session['user_id'],table))
        orders = rows.fetchall()
        
        # total price
        total = 0
        for order in orders:
            total += order[2] * order[3]
        
        # update status order to 3
        db.execute('UPDATE orders SET status=? WHERE user_id=? AND table_name=?', (3, session['user_id'], table))
        
        # commit to database
        db.commit()
        
        # line token from database
        rows = db.execute('SELECT token FROM line_token WHERE user_id=?', (session['user_id'],))
        line = rows.fetchone()
        line = line[0]
        
        # send line message
        send_line(line, f'\nBill from table {table}\n ---- \n Total : {total}')
        
        return redirect(url_for('history'))
    
    else:
        return redirect(url_for('history'))


@app.route('/history')
def history():
    
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    table = request.form.get('table')
        
    # orders from database
    rows = db.execute('SELECT orders.id,items.name,items.price,orders.quantity,orders.comment,orders.status,orders.timestamp FROM orders INNER JOIN items ON orders.item_id=items.id WHERE orders.user_id=? AND orders.status >= 3 ORDER BY orders.timestamp DESC', (session['user_id'],))
    orders = rows.fetchall()
        
    # total price
    total = 0
    for order in orders:
        total += order[2] * order[3]
        
    return render_template('history.html', table=table, orders=orders, total=total)

@app.route('/setting', methods=['GET', 'POST'])
def setting():

    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    # line token from database
    rows = db.execute(
        'SELECT token FROM line_token WHERE user_id=?', (session['user_id'],))
    line = rows.fetchone()

    # if line token is exist then show line token else show empty string
    if line:
        line = line[0]
    else:
        line = 'empty'

    # table from database
    rows = db.execute(
        'SELECT quantity FROM shop_table WHERE user_id=?', (session['user_id'],))
    table = rows.fetchone()

    # if table is exist then show table else show empty string
    if table:
        table = table[0]
    else:
        table = 'empty'

    # items from database
    rows = db.execute(
        'SELECT id,name,price,status FROM items WHERE user_id=?', (session['user_id'],))
    items = rows.fetchall()


    return render_template('setting.html', line=line, table=table, items=items)


@app.route('/profile')
def profile():
    
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    rows = db.execute('SELECT * FROM users WHERE id=?', (session['user_id'],))
    user = rows.fetchone()
    
    user = {
        'id': user[0],
        'username': user[1],
        'password': user[2],
        'email': user[3],
        'shopname': user[4]
    }
    
    return render_template('profile.html', user=user)


@app.route('/editprofile', methods=['GET', 'POST'])
def editprofile():
    
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        email = request.form.get('email')
        shopname = request.form.get('shopname')
        
        if password1 == password2 or password1 == '' or password2 == '':
            db.execute('UPDATE users SET password=?,email=?,shopname=? WHERE id=?', (password1,email,shopname,session['user_id']))
            db.commit()
            
            flash(1)
        
            return redirect(url_for('profile'))
        
        else:
            
            flash(0)
            
            return redirect(url_for('profile'))
    
    else:
        return redirect(url_for('profile'))
        

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        email = request.form.get('email')
        shopname = request.form.get('shopname')

        
        if password1 == password2:
            # check username on database if exist then return error else insert to database
            rows = db.execute('SELECT id FROM users WHERE username=?', (username,))
            user_id = rows.fetchone()
            if user_id:
                flash(0)
                return render_template('register.html')
            else:
                db.execute('INSERT INTO users (username,password,email,shopname) VALUES (?,?,?,?)', (username,password1,email,shopname))
                db.commit()
                
                flash(1)
                
                return render_template('register.html')

    return render_template('/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        rows = db.execute(
            'SELECT id,shopname FROM users WHERE username=? AND password=?', (username, password))
        user = rows.fetchone()

        if user:
            session['user_id'] = user[0]
            session['name'] = user[1]
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message='Username or password is incorrect')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/menu', methods=['GET'])
def menu():
    
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    table = request.args.get('table')
        
    # items from database
    rows = db.execute('SELECT id,name,price FROM items WHERE user_id=? AND status=?', (session['user_id'], 1))
    items = rows.fetchall()
    
    # orders from database
    rows = db.execute('SELECT orders.id,items.name,items.price,orders.quantity,orders.comment,orders.status FROM orders INNER JOIN items ON orders.item_id=items.id WHERE orders.user_id=? AND table_name=? AND orders.status <= 2', (session['user_id'],table))
    orders = rows.fetchall()

    # total price
    total = 0
    for order in orders:
        total += order[2] * order[3]

    
    return render_template('menu.html',table=table, items=items, orders=orders, total=total)

@app.route('/')
def index():     
    if not session.get('user_id'):
        return redirect(url_for('login'))
     # table from database
    rows = db.execute('SELECT quantity FROM shop_table WHERE user_id=?', (session['user_id'],))
    table = rows.fetchone()
    
    # if table is exist then show table else show empty string
    if table:
        table = table[0]
    else:
        table = 0
    
    return render_template('index.html' , table=table)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
    Server(app.wsgi_app)
