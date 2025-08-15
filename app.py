from flask import Flask , request,jsonify,g,render_template,url_for,redirect,session
from plyer import notification
from werkzeug.security import generate_password_hash,check_password_hash
import sqlite3
app = Flask(__name__)
app.secret_key='supersecretkey'
DATABASE = 'hook.db'
@app.route('/')
def home():
    return render_template("home.html")
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        u_name = request.form["username"]
        pw = request.form["password"]
        conn = sqlite3.connect('auth.db')
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?",(u_name,))
        user = c.fetchone()
        conn.close()
        if not user:
            return """
                    <script>
                    alert("Invalid Credentials");
                    window.history.back();
                    </script>"""
        if user and check_password_hash(user[0],pw):
            session["user"]=u_name
            return redirect(url_for("hooks"))
        else:
            return """
                    <script>
                    alert("Invalid Credentials");
                    window.history.back();
                    </script>"""
    return render_template('login.html')
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u_name = request.form['username']
        pw = request.form['password']
        hashed_pw = generate_password_hash(pw)
        try:
            conn = sqlite3.connect('auth.db')
            c = conn.cursor()
            c.execute('INSERT INTO users (username,password) VALUES (?,?)',(u_name,hashed_pw))
            conn.commit()
            conn.close()
            return render_template('Registered.html',u_name = u_name)
        except sqlite3.IntegrityError:
            return """
                    <script>
                    alert("Username already exists");
                    window.history.back();
                    </script>"""
    return render_template("register.html")
def get_db():
    if'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db
def send_not(title,message):
    notification.notify(title = title,message = message , timeout = 5)
def add_user(id,repo_name,u_name,Added="",Removed="",Modified="",timestamp=""):
    db = get_db()
    cursor = db.execute('INSERT INTO commits(id,repo_name,Committer,Added,Removed,Modified,timestamp) VALUES (?,?,?,?,?,?,?)',(id,repo_name,u_name,Added,Removed,Modified,timestamp))
    db.commit()
    db.close()
    return f"Added {id}"
@app.route("/webhook",methods = ["POST"])
def webhook():
    data = request.json
    repo = data["repository"]
    repo_name = repo["name"]
    commit = data["head_commit"]
    timestamp = commit["timestamp"]
    id = commit["id"]
    print("Webhook Recieved")
    print(f"id : {id}")
    print(f"repo_name : {repo_name}")
    print(f"Committer username : {commit['committer']['username']}")
    added_str = ','.join(commit['added'])
    removed_str = ','.join(commit['removed'])
    modified_str = ','.join(commit['modified'])
    add_user(id,repo_name,commit['committer']['username'],added_str,removed_str,modified_str,timestamp)
    mes = []
    if commit["added"]:
        for add in commit["added"]:
            print(f"Added : {add}")
            mes.append(f"Added {add}")
    if commit["removed"]:
        for rem in commit["removed"]:
            print(f"Removed : {rem}")
            mes.append(f"Removed {rem}")
    if commit["modified"]:
        for mod in commit["modified"]:
            print(f"Modified : {mod}")
            mes.append(f"Modified {mod}")
    send_not("Webhook Recieved" , "\n".join(mes))
    return jsonify({"Status" : "Recieved"}),200
@app.route('/Hooks',methods=["GET","POST"])
def hooks():
    if "user" in session:
        db=get_db()
        from_date=None
        to_date = None
        if request.method =='POST':
            from_date = request.form['From_Date']
            to_date = request.form['To_Date']
        if from_date and to_date:
            cursor=db.execute('SELECT * FROM commits WHERE timestamp >= ? and timestamp <=?',(from_date,to_date))
        elif from_date or to_date:
            if from_date:
                cursor=db.execute('SELECT * FROM commits WHERE timestamp >=?',(from_date,))
            if to_date:
                cursor=db.execute('SELECT * FROM commits WHERE timestamp <=?',(to_date,))
        else:
            cursor = db.execute('SELECT * FROM commits')
        commits = cursor.fetchall()
        return render_template('webhook.html',commits = commits,username = session["user"])
    return render_template('Notfound.html')
@app.route('/logout',methods=['GET','POST'])
def logout():
    session.pop("user",None)
    return redirect(url_for("home"))
@app.route('/search',methods=["GET","POST"])
def search():
    query = request.form["query"]
    if not query:
        return redirect(url_for("hooks"))
    db = get_db()
    cursor = db.execute("""SELECT * FROM commits WHERE 
                        repo_name LIKE ?
                        OR id LIKE ?
                        OR Committer LIKE ?
                        OR Added LIKE ?
                        OR Removed LIKE ?
                        OR Modified LIKE?
                        OR TimeStamp LIKE?""",tuple('%'+query+'%' for _ in range(7)))
    commits = cursor.fetchall()
    return render_template('webhook.html',commits = commits,username = session["user"])
@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db',None)
    if db is not None:
        db.close()
if __name__ == "__main__":
    app.run(port=5000,debug = True)