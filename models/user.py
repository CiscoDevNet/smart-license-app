import sqlite3
from models.sl_logger import SlLogger

logger = SlLogger.get_logger(__name__)


class UserModel:
    def __init__(self, _id, username, password, pswd_hint):
        self.id = _id
        self.username = username
        self.password = password
        self.pswd_hint = pswd_hint

    @classmethod
    def create_connection(cls, db_file):
        connection = None
        try:
            connection = sqlite3.connect(db_file)
            logger.info('Connection to ' + db_file + ' is successful')
        except Exception as e:
            logger.error(e)
        return connection

    @classmethod
    def find_by_username(cls, username):
        connection = UserModel.create_connection('data.db')
        if connection:
            cursor = connection.cursor()
            query = "SELECT * FROM users WHERE username=?"
            logger.info("Querying users table in data.db on username field")
            result = cursor.execute(query, (username,))
            row = result.fetchone()
            if row:
                user = cls(*row)
            else:
                user = None
            connection.close()
            return user

    @classmethod
    def find_by_id(cls, _id):
        connection = UserModel.create_connection('data.db')
        if connection:
            cursor = connection.cursor()
            query = "SELECT * FROM users WHERE id=?"
            logger.info("Querying users table in data.db on id field")
            result = cursor.execute(query, (_id,))
            row = result.fetchone()
            if row:
                user = cls(*row)
            else:
                user = None

            connection.close()
            return user

    @classmethod
    def get_password_by_username(cls, username, password):
        connection = UserModel.create_connection('data.db')
        if connection:
            cursor = connection.cursor()
            query = "SELECT " + password + " FROM users WHERE username=?"
            logger.info("Querying users table in data.db on username field to get " + password)
            result = cursor.execute(query, (username,))
            row = result.fetchone()[0]
            connection.close()
            return row

    @classmethod
    def user_exists(cls, username):
        connection = UserModel.create_connection('data.db')
        if connection:
            cursor = connection.cursor()
            query = "SELECT COUNT(*) FROM users WHERE username=?"
            logger.info("Querying users table in data.db to check if username exists")
            result = cursor.execute(query, (username,))
            row = result.fetchone()[0]
            connection.close()
            return row

    @classmethod
    def update_password(cls, username, newPassword):
        connection = UserModel.create_connection('data.db')
        if connection:
            cursor = connection.cursor()
            query = "UPDATE users SET password=? WHERE username=?"
            logger.info("Updating user table with new hashed password")
            cursor.execute(query, (newPassword, username))
            connection.commit()
            connection.close()
