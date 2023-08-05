from src.constants.http_status_codes import *
from flask  import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

import validators
from flask_jwt_extended import jwt_required, \
create_access_token, create_refresh_token, get_jwt_identity
from flasgger import  swag_from

from src.database import User, db

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth.post('/register')
@swag_from('./docs/auth/register.yaml')
def register():
    #grab the json first===
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if len(password) < 6:
        return jsonify({'error':"Password is too short"}, HTTP_400_BAD_REQUEST)
    if len(username) < 3:
        return jsonify({'error':"Username is too short"}, HTTP_400_BAD_REQUEST)
    if not username.isalnum() or " " in username:
        return jsonify({'error':"Username should be alphanumeric, also no spaces"}, 
            HTTP_400_BAD_REQUEST
        )
    if not validators.email(email):
        return jsonify({'error':"Email is not valid"}, 
            HTTP_400_BAD_REQUEST
        )
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error':"Email is taken"}, 
            HTTP_409_CONFLICT
        )
    
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error':"Email is taken"}, 
            HTTP_409_CONFLICT
        )
    
    #after condition is okay go ahead and hash the user's password
    pwd_hash = generate_password_hash(password)
    user=User(username=username, password=pwd_hash, email=email)
    db.session.add(user)
    db.session.commit()#commit to make sure that changes are saved
    return jsonify({
        'message':"User created",
        'user':{
            'username':username,"email":email
        }
    },HTTP_201_CREATED)

#===route to login user===
@auth.post('/login')
@swag_from('./docs/auth/login.yaml')
def login():
    data = request.json
    email = data.get('email', '')
    password = data.get('password', '')

    user=User.query.filter_by(email=email).first()
    if user:
        is_pass_correct = check_password_hash(user.password,password)
        #==checking if the password is correct
        if is_pass_correct:
            #go ahead and create an access token for them
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)

            return jsonify({
                'user':{
                    'refresh':refresh,
                    'access':access,
                    'username':user.username,
                    'email':user.email
                }
            }, HTTP_200_OK)
    return jsonify({'error':'Wrong credentials'}, HTTP_401_UNAUTHORIZED)

@auth.get("/me")
@jwt_required() #meant that the user cant access the resource without token
def me():
    #import pdb
    #pdb.set_trace()#for debugging purposes
    user_id = get_jwt_identity()#so basically this helps us get the current user
    user=User.query.filter_by(id=user_id).first()
    return jsonify({
        'username':user.username,
        'email':user.email
    }, HTTP_200_OK)


@auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        'access': access
    }, HTTP_200_OK)

