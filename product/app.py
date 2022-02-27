import os
import sys
import argparse
from datetime import datetime
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


class Proxy(db.Model):
    __table_args__ = (db.UniqueConstraint('ip', 'port', name='uix_1'),)
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100), nullable=False)
    port = db.Column(db.String(100), nullable=False)
    is_valid = db.Column(db.Boolean, default=False)
    last_check_date = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.Text)
    is_mobile_proxy = db.Column(db.Boolean)
    is_data_center_proxy = db.Column(db.Boolean)
    is_home_proxy = db.Column(db.Boolean)

    def __init__(self, ip, port, is_valid, type, is_mobile_proxy, is_data_center_proxy, is_home_proxy):
        self.ip = ip
        self.port = port
        self.is_valid = is_valid
        self.type = type
        self.is_mobile_proxy = is_mobile_proxy
        self.is_data_center_proxy = is_data_center_proxy
        self.is_home_proxy = is_home_proxy

    def __repr__(self):
        return "<Proxy: id = {id}; ip = {ip}; port = {port};is_valid = {is_valid};last_check_date = {last_check_date};\
        type = {type};is_mobile_proxy = {is_mobile_proxy};is_data_center_proxy = {is_data_center_proxy};" \
               "is_home_proxy = {is_home_proxy};>".format(id=self.id, ip=self.ip, port=self.port,
                                                          is_valid=self.is_valid,
                                                          last_check_date=self.last_check_date, type=self.type,
                                                          is_mobile_proxy=self.is_mobile_proxy,
                                                          is_data_center_proxy=self.is_data_center_proxy,
                                                          is_home_proxy=self.is_home_proxy)


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
            is_valid_proxy = is_valid(ip + ':' + port)
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

    # from models.proxy import Proxy

    db.create_all()
    db.session.commit()

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, help='host for running flask', default="0.0.0.0")
    args = parser.parse_args()

    app.run(host=args.host, debug=True)
