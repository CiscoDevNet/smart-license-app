from flask import request, send_from_directory
# from slta_resful import app
from flask_restful import Resource


class Serveslcsv(Resource):
    def get(self):
        return send_from_directory('frontend/build', request.path[1:])


class Serveslrcsv(Resource):
    def get(self):
        return send_from_directory('frontend/build', request.path[1:])
