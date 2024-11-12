import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from waitress import serve
from flask_compress import Compress


def create_app():
    start_date = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
    app = Flask(__name__, instance_relative_config=True)
    app.config['JSON_SORT_KEYS'] = False
    print('start_server')
    compress = Compress()
    compress.init_app(app)

    CORS(app)
    Bootstrap(app)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.errorhandler(404)
    def page_not_found(error):
        return 'This page does not exist', 404

    @app.route('/', methods=['GET'], endpoint='status')
    def hello():
        now = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
        return jsonify({'last_server_update': start_date, 'date_now': now, 'status': 200})

    @app.route('/forecasts', methods=['GET'], endpoint='forecasts')
    def get_forecasts():
        now = request.args.get('now')
        then = request.args.get('then')

        return jsonify({})

    @app.route('/tomorrow', methods=['GET'], endpoint='tomorrow')
    def get_tomorrow():
        now = request.args.get('now')

        return jsonify({})

    return app


if __name__ == "__main__":
    serve(create_app(), host="0.0.0.0", port=5000)
