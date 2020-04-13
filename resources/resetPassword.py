from flask_restful import Resource, reqparse
from flask_bcrypt import Bcrypt
from models.user import UserModel
from models.sl_logger import SlLogger


logger = SlLogger.get_logger(__name__)


class ResetPassword(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('oldPassword',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('newPassword',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    def post(self):
        data = ResetPassword.parser.parse_args()
        bcrypt = Bcrypt()

        if UserModel.user_exists(data['username']) == 0:
            logger.error("User with this username doesn't exist")
            return {"message": "User with this username doesn't exist!"}, 401

        stored_password = UserModel.get_password_by_username(data['username'], "password")
        check_password = bcrypt.check_password_hash(stored_password, data['oldPassword'])
        if check_password:
            logger.info("Password matched")
            hashed_password = bcrypt.generate_password_hash(data['newPassword']).decode('utf-8')
            try:
                UserModel.update_password(data['username'], hashed_password)
                logger.info("message:" "Password updated")
                return {"message": "Password updated"}, 200
            except Exception as e:
                logger.error(e)
                logger.error("Update password operation failed!", exc_info=True)
                return {"message": "Update password operation failed!"}, 500
        else:
            return {"message": "Old password doesn't match"}, 403
