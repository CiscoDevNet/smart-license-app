from flask_bcrypt import Bcrypt
from models.user import UserModel
from models.sl_logger import SlLogger


logger = SlLogger.get_logger(__name__)

users = [
    UserModel(1, 'nikul', 'asdfg', "hint:answer")
]


def authenticate(username, password):
    bcrypt = Bcrypt()
    user = UserModel.find_by_username(username)
    if user and bcrypt.check_password_hash(user.password, password):
        logger.info("User authentication is successful")
        return user


def identity(payload):
    user_id = payload['identity']
    return UserModel.find_by_id(user_id)
