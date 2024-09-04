from sqlite3 import IntegrityError
from flask import request, jsonify, render_template, make_response
from src import app,db,ALLOWED_EXTENSIONS,bcrypt,create_access_token,csrf
from src.model import User,Subject
from werkzeug.utils import secure_filename
import os
from .ocr_model.resource.main import doRequestOCR


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def defaultpage():
    return render_template("default.html")

@app.route("/info/<string:email>", methods=["GET"])
def getUserInfo(email):
    user = User.query.filter_by(email=email).first()

    if user:
        subjects = [
            {
                "section": subject.section,
                "id":subject.id,
                "name": subject.name,
                "unit": subject.unit,
                "grade": subject.grade
            }
            for subject in user.subjects
        ]

        user_info = {
            "email": user.email,
            "filename": user.filename,
            "subjects": subjects
        }

        return make_response(jsonify(user_info), 200)
    else:
        return make_response(jsonify({
            "message": "User not found"
        }), 404)


@app.route("/doOCR/<string:email>", methods=['PATCH'])
@csrf.exempt
def doOCR(email):

    user = User.query.filter_by(email=email).first()

    front, back = doRequestOCR(user.filename)
    
    subjects = front

    print(type(subjects))
    print(subjects)

    ready_subjects = []
    for i in range(1, int(subjects.get("length")) + 1):
        temp = subjects['data'].get(i)
        if temp:
            subject = Subject(
                id = temp.get("id"),
                unit=temp.get("unit"),
                name=temp.get("name"),
                grade=temp.get("grade")
            )
            ready_subjects.append(subject)

    if user:
        user.subjects = ready_subjects

        try:
            db.session.commit()
            return make_response(jsonify({
                "message": "Successful OCR transcript"
            }), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({
                "message": str(e)
            }), 500)
    else:
        return make_response(jsonify({
            "message": "User not found"
        }), 404)


@app.route("/register",methods=["POST"])
@csrf.exempt
def register():
    if not request.json:
        return make_response(jsonify({
            "message":"there is empty request"
        }),400)

    email = request.json.get("email")
    password = request.json.get("password")

    if not email or not password:
        return jsonify({
            "message":"need to fill every data before submit"
        },400)

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_users = User(email=email, password=hashed_password)
    

    try:
        db.session.add(new_users)
        db.session.commit()

        message = "User created successfully"
        data = {
            "id": new_users.id,
            "email": new_users.email,
            "password": new_users.password,
            "filename":new_users.filename
            }
        return make_response(jsonify({
            "message":message,
            "data":data
        }))
    
    except IntegrityError as e:
        db.session.rollback()
        return make_response(jsonify({"message": "Email already exists"}), 400)
    
    except Exception as e :
        db.session.rollback()
        return make_response(jsonify({"message":str(e)}), 500)

@app.route('/login', methods=['POST'])
@csrf.exempt
def login():
    email = request.json.get("email")
    password = request.json.get("password")

    if not email and not password:
        return make_response(jsonify({
            "message":"Must fill email or password before login"
        },400))
    
    user = User.query.filter_by(email=email).first()

    if not user :
        return make_response(jsonify({
            "message":"User not found"
        }),404)
    
    if not bcrypt.check_password_hash(user.password, password):
        return make_response(
            jsonify({
                "message":"Invalid password"
            }),401
        )
    
    token = create_access_token(identity=email)
    return jsonify({
        "email":email,
        "token": token
        }), 200

@app.route("/upload/<string:email>", methods=['PATCH'])
@csrf.exempt
def upload(email):
    user = User.query.filter_by(email = email).first()

    if not user:
        return make_response(jsonify(
            {
                "message":"User not found"
            }
        ),404
        )
    
    file = request.files['file']

    if not file:
        return make_response(jsonify(
            {
                "message":"There is no file part"
            },401
        ))
    
    if file.filename == "":
        return make_response(jsonify(
            {
                "message":"There is empty request"
            },402
        ))
    elif file and allowed_file(file.filename):


        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        user.filename = filename


        try :
            db.session.commit()
            return make_response(jsonify(
                {
                    "message":"Successful upload file"
                },200
            ))
        except Exception as e :
            db.session.rollback()
            return make_response(jsonify({"message":str(e)}), 500)


        
        