import datetime
from sqlite3 import IntegrityError
from flask import request, make_response, jsonify
import jwt
from src import bcrypt, db, JWT_SECRET
from ..model import User
from . import auth_group

@auth_group.route("/register",methods=["POST"])
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
    


@auth_group.route('/login', methods=['POST'])
def login():
    email = request.json.get("email")
    password = request.json.get("password")

    if not email and not password:
        return make_response(jsonify({
            "message":"Must fill email or password before login"
        }),400)
    
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
    
    # token = create_access_token(identity=email)

    payload = {
            "email":user.email,
            "exp":datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=48)
        }

    token = jwt.encode(payload=payload, key=JWT_SECRET.encode("utf-8"), algorithm='HS256')

    response = make_response(jsonify({
            "data":{
                "email":user.email,
                "token":token
            },
            "message":"Successful Login!"
        }), 200)

    return response