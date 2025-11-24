from functools import wraps
from sqlite3 import IntegrityError
from flask import request, jsonify, render_template, make_response
import jwt
from src import app,db,ALLOWED_EXTENSIONS,JWT_SECRET
from ..model import User,Subject, Report
from werkzeug.utils import secure_filename
import os
from ..ocr_model.resource.main import doRequestOCR
from . import user_group


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def jwt_check(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        # token = request.cookies.get('auth_token')

        if not token:
            return make_response(
                jsonify({
                    "message":"Token is missing"
                }),401
            )

        try:
            token = token.split()[1]
            payload = jwt.decode(token, JWT_SECRET.encode("utf-8"), algorithms=["HS256"])

            request.email = payload.get("email")

        except jwt.ExpiredSignatureError:
            return make_response(jsonify({
                "message":"Token has expired"
            }),401)
        
        except jwt.InvalidTokenError as e:
            print(e)
            return make_response(jsonify({
                "message":"Invalid Token"
            }),401)
        return f(*args, **kwargs)
    return decorated

@user_group.route("/")
def defaultpage():
    return render_template("default.html")

@user_group.get("/<string:email>")
@jwt_check
def getUserInfo(email):

    if request.email != email:
        return make_response(jsonify({
            "message":"Token doesn't match"
        }),403)

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
            "subjects": subjects,
        }

        return make_response(jsonify(user_info), 200)
    else:
        return make_response(jsonify({
            "message": "User not found"
        }), 404)


@user_group.patch("/doOCR/<string:email>")
@jwt_check
def doOCR(email):

    if request.email != email:
        return make_response(jsonify({
            "message":"Token doesn't match"
        }),403)

    user = User.query.filter_by(email=email).first()

    if not user :
        return make_response(jsonify({
            "message":"User not found"
        }),400)
    
    if user.filename == "" or not user.filename:
        return make_response(jsonify({
            "message":"User doesn't upload file yet"
        }),400)
    
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


@user_group.patch("/upload/<string:email>")
@jwt_check
def upload(email):

    if request.email != email:
        return make_response(jsonify({
            "message":"Token doesn't match"
        }),403)
    
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
            }
        ),401)
    
    if file.filename == "":
        return make_response(jsonify(
            {
                "message":"There is empty request"
            }
        ),402)
    elif file and allowed_file(file.filename):


        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        user.filename = filename


        try :
            db.session.commit()
            return make_response(jsonify(
                {
                    "message":"Successful upload file"
                }
            ),200)
        except Exception as e :
            db.session.rollback()
            return make_response(jsonify({"message":str(e)}), 500)


@user_group.get("/getavg/<string:email>")
@jwt_check
def getAVG(email): 

    if request.email != email:
        return make_response(jsonify({
            "message":"Token doesn't match"
        }),403)
    
    user = User.query.filter_by(email=email).first()

    if not user:
        return make_response(jsonify({
            "message": "User not found"
        }),404)

    if len(user.subjects) == 0:
        return make_response(jsonify({
            "message": "Subjects not found"
        }),404)
    
    groupMap = {
                    'ท': 'ภาษาไทย',
                    'ส': 'สังคมศึกษา',
                    'ค': 'คณิตศาสตร์',
                    'ว': 'วิทยาศาสตร์',
                    'อ': 'ภาษาต่างประเทศ',
                    'พ': 'สุขศึกษาและพลศึกษา',
                    'ศ': 'ศิลปะ',
                    'ง': 'การงานอาชีพ',
                    'I': 'การศึกษาค้นคว้าด้วยตนเอง',
                    'ญ': 'ภาษาต่างประเทศ',
                    'จ': 'ภาษาต่างประเทศ',
                    'ฝ': 'ภาษาต่างประเทศ',
                    'ย': 'ภาษาต่างประเทศ',

                }
    
    data = {
        'ภาษาไทย': {
            'gpax':0,
            'unit':0,
            'quantity':0
        },
        'สังคมศึกษา': {
            'gpax':0,
            'unit':0,
            'quantity':0
        },
        'คณิตศาสตร์': {
            'gpax':0,
            'unit':0,
            'quantity':0
        },
        'วิทยาศาสตร์': {
            'gpax':0,
            'unit':0,
            'quantity':0
        },
        'ภาษาต่างประเทศ': {
            'gpax':0,
            'unit':0,
            'quantity':0
        },
        'สุขศึกษาและพลศึกษา': {
            'gpax':0,
            'unit':0,
            'quantity':0
        },
        'ศิลปะ': {
            'gpax':0,
            'unit':0,
            'quantity':0
        },
        'การงานอาชีพ': {
            'gpax':0,
            'unit':0,
            'quantity':0
        },
        'การศึกษาค้นคว้าด้วยตนเอง': {
            'gpax':0,
            'unit':0,
            'quantity':0
        },
        'อื่นๆ':{
            "subjects":[]
        }
    }

    totalUnit = 0
    totalGpax = 0

    for subject in user.subjects:
        cate = groupMap.get(subject.id[0], 'อื่นๆ')

        if cate == 'อื่นๆ':
            data[cate]['subjects'].append({
                "id": subject.id,
                "name": subject.name,
                "unit": subject.unit,
                "grade": subject.grade
            })
            continue
        else:
            score = data[cate]['gpax'] * data[cate]['unit'] + subject.grade * subject.unit
            data[cate]['unit'] += subject.unit
            data[cate]['gpax'] = round(score / data[cate]['unit'], 3)
            
        totalGpax = (totalGpax * totalUnit) + (subject.grade * subject.unit)
        totalUnit += subject.unit

        if totalUnit > 0:
            totalGpax = round(totalGpax / totalUnit, 3)

    return jsonify({
        "message": "Successful get avg",
        "data": {
            "totalGpax": totalGpax,
            "totalUnit": totalUnit,
            "categoryList": list(set(groupMap.values())),
            "categoryData": data
        }
    }), 200



@user_group.post("/report/<string:email>")
@jwt_check
def report(email):

    if request.email != email:
        return make_response(jsonify({
            "message":"Token doesn't match"
        }),403)
    

    user = User.query.filter_by(email=email).first()

    if not user:
        return make_response(jsonify({
            "message": "User not found"
        }),404)
    

    category = request.json.get("category")
    report = str(request.json.get("report"))


    if not category or not report or report.strip() == "":
        return make_response(jsonify({
            "message":"Missing category or report message"
        }),400)


    new_report = Report(category=category, report = report, user_id = user.id)


    try:
        db.session.add(new_report)
        db.session.commit()

        return make_response(jsonify({
            "message": "Report submitted successfully"
        }), 200)
    except Exception as e:
        return make_response(jsonify({
            "message":e
        }),500)


@user_group.get("/report/<string:email>")
@jwt_check
def get_report(email):

    if request.email != email:
        return make_response(jsonify({
            "message":"Token doesn't match"
        }),403)
    
    user = User.query.filter_by(email=email).first()

    if not user:
        return make_response(jsonify({
            "message": "User not found"
        }),404)
    

    if len(user.reports) == 0:
        return make_response(jsonify({
            "message":"There is no report"
        }),400)
    
    data = []
    
    for report in Report.query.filter_by(user_id = user.id).all():
        data.append({
            "category":report.category,
            "report": report.report
        })

    return make_response(jsonify({
        "data": data
    }),200)