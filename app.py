import os
import sys
import argparse
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(basedir, "utils"))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "db.sqlite")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ma = Marshmallow(app)




class ProxySchema(ma.Schema):
    class Meta:
        fields = ('id', 'ip', 'port', 'is_valid', 'last_check_date',
                  'type', 'is_mobile_proxy', 'is_data_center_proxy', 'is_home_proxy')


proxy_schema = ProxySchema()
proxies_schema = ProxySchema(many=True)


@app.route('/proxy', methods=['POST', 'GET'])
def manage_proxy():
    if request.method == 'POST':
        if isinstance(request.json, dict):
            js = [request.json]
        elif isinstance(request.json, list):
            js = request.json
        proxies = ()
        for js_el in js:
            ip = js_el['ip']
            port = js_el['port']
            type = js_el['type']
            is_mobile_proxy = js_el['is_mobile_proxy']
            is_data_center_proxy = js_el['is_data_center_proxy']
            is_home_proxy = js_el['is_home_proxy']
            is_valid_proxy = is_valid(host=ip, port=port)
            if not isinstance(is_valid_proxy, bool):
                is_valid_proxy = False
            new_proxy = Proxy(ip=ip, port=port, is_valid=is_valid_proxy, type=type, is_mobile_proxy=is_mobile_proxy,
                              is_data_center_proxy=is_data_center_proxy, is_home_proxy=is_home_proxy)
            db.session.add(new_proxy)
            db.session.commit()
            proxies += (new_proxy,)
        return proxies_schema.jsonify(proxies)
    else:
        all_proxies = Proxy.query.all()
        result = proxies_schema.dump(all_proxies)
        return jsonify(result)


@app.route("/proxy/fill", methods=['POST'])
def fill_db():
    proxs = get_proxies()
    log("Collected {} valid proxies".format(len(proxs)))
    proxies = ()
    for p in proxs:
        host, port = p.split(':')
        new_proxy = Proxy(ip=host, port=port, is_valid=True, type=None, is_mobile_proxy=False,
                          is_data_center_proxy=False, is_home_proxy=False)
        try:
            db.session.add(new_proxy)
            db.session.commit()
        except:
            db.session.rollback()
        proxies += (new_proxy,)
    return proxies_schema.jsonify(proxies)


if __name__ == '__main__':
    from utils.parse_into_db import get_proxies
    from utils.validation import is_valid
    from utils.logger import log
    from models.proxy import Proxy
    from utils.validation import check_validity

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, help='host for running flask', default="0.0.0.0")
    args = parser.parse_args()

    db.create_all()

    check_validity()

    app.run(host=args.host, debug=True)
