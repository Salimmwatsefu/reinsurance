from flask_restful import Resource, Api, reqparse
from flask import Blueprint
from app.services.auth_service import create_user, authenticate, logout, get_current_user
from werkzeug.exceptions import BadRequest, Unauthorized
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint for auth routes
auth_bp = Blueprint('auth', __name__)
api = Api(auth_bp)

class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help="Email cannot be blank")
        parser.add_argument('first_name', type=str, required=True, help="First name cannot be blank")
        parser.add_argument('last_name', type=str, required=True, help="Last name cannot be blank")
        parser.add_argument('password', type=str, required=True, help="Password cannot be blank")
        parser.add_argument('role', type=str, required=True, help="Role cannot be blank")
        args = parser.parse_args()

        try:
            user = create_user(
                email=args['email'],
                first_name=args['first_name'],
                last_name=args['last_name'],
                password=args['password'],
                role=args['role']
            )
            logger.info("User registered: %s", args['email'])
            return {
                'message': 'User created successfully',
                "user": user.to_dict()
            }, 201
        except BadRequest as e:
            logger.error("Registration error: %s", str(e))
            return {'message': str(e)}, 400

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help="Email cannot be blank")
        parser.add_argument('password', type=str, required=True, help="Password cannot be blank")
        args = parser.parse_args()

        try:
            result = authenticate(args['email'], args['password'])
            logger.info("User logged in: %s", args['email'])
            return result, 200
        except Unauthorized as e:
            logger.error("Login error: %s", str(e))
            return {'message': str(e)}, 401

class Logout(Resource):
    def post(self):
        try:
            result = logout()
            logger.info("User logged out")
            return result, 200
        except Exception as e:
            logger.error("Logout error: %s", str(e))
            return {'message': str(e)}, 400

class Profile(Resource):
    def get(self):
        try:
            user = get_current_user()
            return {'user': user.to_dict()}, 200
        except Unauthorized as e:
            return {'message': str(e)}, 401

# Add resources to API
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(Profile, '/profile')
