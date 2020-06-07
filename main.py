from flask import Flask, Response, request, url_for, redirect
from flask_restplus import Api, Resource, fields
import json
from handler.ssh_service import SshHandler
from flask_cors import CORS, cross_origin
from micro_kit import CustomResponse

app = Flask(__name__)
cors = CORS(app)

api = Api(app=app)
ns_conf = api.namespace('ssh', description='SSH operations')

handler = SshHandler()
import time


@ns_conf.route("/host")
class Host(Resource):
    def get(self):
        output = handler.read_config()
        time.sleep(4)
        return CustomResponse(output)

    @api.doc(responses={200: 'OK', 400: 'Invalid Argument'})
    def post(self):
        data = json.loads(request.data.decode('utf-8'))
        output, status = handler.add_config(data)
        return CustomResponse(output)


@ns_conf.route("/host/<string:host>")
class HostEdit(Resource):

    def put(self, host):
        data = json.loads(request.data.decode('utf-8'))
        output, status = handler.edit_config(host, data)
        return CustomResponse(output)

@ns_conf.route("/local-forward")
class HostEdit(Resource):

    def get(self):
        output, status = handler.get_local_forward()
        return CustomResponse(output)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
