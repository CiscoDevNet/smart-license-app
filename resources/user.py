import sqlite3
from flask_restful import Resource, reqparse
from flask_bcrypt import Bcrypt
from models.user import UserModel
from models.sl_logger import SlLogger


logger = SlLogger.get_logger(__name__)


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    parser.add_argument('pswd_hint',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    def post(self):
        data = UserRegister.parser.parse_args()
        bcrypt = Bcrypt()

        if UserModel.find_by_username(data['username']):
            logger.error("User with that username already exists")
            return {"message": "User with that username already exists."}, 400

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "INSERT INTO users VALUES (NULL, ?, ?, ?)"

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        hashed_pswd_hint = bcrypt.generate_password_hash(data['pswd_hint']).decode('utf-8')
        cursor.execute(query, (data['username'], hashed_password, hashed_pswd_hint))

        connection.commit()
        connection.close()

        logger.info("User created successfully.")
        return {"message": "User created successfully."}, 201
