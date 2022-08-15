from crypt import methods
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import random


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///projects.db"
db = SQLAlchemy(app)


class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prjt_name = db.Column(db.String(50), nullable=False)
    prjt_desc = db.Column(db.String(1000), nullable=False)
    prjt_per = db.Column(db.Integer, nullable=False)
    prjt_team = db.Column(db.String(1000), nullable=False)
    prjt_guide = db.Column(db.String(50), nullable=False)
    prjt_git = db.Column(db.String(200), nullable=False)
    prjt_full = db.Column(db.String(100), nullable=False)
    prjt_thumb = db.Column(db.String(100), nullable=False)
    prjt_token = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return "<Task %r>" % self.id


def generate_token():
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
               'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
               'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    characters = []
    for i in range(8):
        characters.append(random.choice(letters))
    for i in range(2):
        characters.append(random.choice(symbols))
    for i in range(5):
        characters.append(random.choice(numbers))
    random.shuffle(characters)
    return "".join(characters)


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        rand_int = random.randint(1, 12)
        rand_int = f"0{rand_int}" if rand_int < 10 else rand_int
        prjt_full = url_for('static', filename=f'images/fulls/{rand_int}.jpg')
        prjt_thumb = url_for('static', filename=f'images/thumbs/{rand_int}.jpg')

        prjt_name = request.form["prjt_name"]
        prjt_desc = request.form["prjt_desc"]
        prjt_per = request.form["prjt_per"]
        prjt_guide = request.form["prjt_guide"]
        prjt_git = request.form["prjt_git"]

        prjt_team = []
        for i in range(1, 5):
            member = f"member_{i}"
            usn = f"usn_{i}"
            if len(request.form[member]) < 1:
                break
            prjt_team.append(request.form[member])
            prjt_team.append(request.form[usn])
        prjt_team = " ".join(prjt_team)

        prjt_token = generate_token()

        new_project = Projects(prjt_name=prjt_name,
                            prjt_desc=prjt_desc,
                            prjt_full=prjt_full,
                            prjt_thumb=prjt_thumb,
                            prjt_per=prjt_per,
                            prjt_guide=prjt_guide,
                            prjt_git=prjt_git,
                            prjt_team=prjt_team, 
                            prjt_token=prjt_token)

        try:
            flash(f"Project Token: {prjt_token}")  
            db.session.add(new_project)
            db.session.commit()
            return redirect("/")
        except:
            return "There was an issue adding your project."

    else:
        projects = Projects.query.order_by(Projects.id).all()
        return render_template("index.html", projects=projects)


@app.route("/delete/<int:id>", methods=["POST", "GET"])
def delete(id):
    project = Projects.query.get_or_404(id)
    if request.form["prjt_token"] == project.prjt_token:
        try:
            db.session.delete(project)
            db.session.commit()
            projects = Projects.query.order_by(Projects.id).all()
            return render_template("./index.html", projects=projects)
        except:
            return "There was a issue deleting your project."
    else:
        return "Incorrect project token."


@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):
    project = Projects.query.get_or_404(id)

    if request.method == "POST":
        if request.form["prjt_token"] == project.prjt_token:
            if len(request.form["prjt_name"]) > 1:
                project.prjt_name = request.form["prjt_name"]
            if len(request.form["prjt_desc"]) > 1:
                project.prjt_desc = request.form["prjt_desc"]
            if len(request.form["prjt_per"]) > 1:
                project.prjt_per = request.form["prjt_per"]
            if len(request.form["prjt_guide"]) > 1:
                project.prjt_guide = request.form["prjt_guide"]
            if len(request.form["prjt_git"]) > 1:
                project.prjt_git = request.form["prjt_git"]

            prjt_team = []
            for i in range(1, 5):
                member = f"member_{i}"
                usn = f"usn_{i}"
                if len(request.form[member]) < 1:
                    break
                prjt_team.append(request.form[member])
                prjt_team.append(request.form[usn])
            if len(prjt_team) > 1:
                project.prjt_team = " ".join(prjt_team)

            try:
                db.session.commit()
                project = Projects.query.get_or_404(id)
                return render_template("project.html", project=project)
            except:
                return "There was an issue updating your project."
        else:
            return "Incorrect project token."
        
    else:
        return render_template("project.html", project=project)


@app.route("/clickme/<int:id>")
def click_me(id):
    project = Projects.query.get_or_404(id)
    try:
        return render_template("project.html", project=project)
    except:
        return redirect("/")

if __name__  == "__main__":
    app.run(debug=True)
