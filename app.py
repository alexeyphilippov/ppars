import os
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "db.sqlite")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

ma = Marshmallow(app)


def log(s):
    print(format(datetime.now(), '%Y-%m-%d %H:%M:%S'), '||', str(s))


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

    def __init__(self, ip, port, type, is_mobile_proxy, is_data_center_proxy, is_home_proxy):
        self.ip = ip
        self.port = port
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


class ProxySchema(ma.Schema):
    class Meta:
        fields = ('id', 'ip', 'port', 'is_valid', 'last_check_date',
                  'type', 'is_mobile_proxy', 'is_data_center_proxy', 'is_home_proxy')


proxy_schema = ProxySchema(strict=True)
proxies_schema = ProxySchema(many=True, strict=True)


@app.route('/proxy', methods=['POST', 'GET'])
def manage_proxy():
    check_validity()
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

            new_proxy = Proxy(ip=ip, port=port, type=type, is_mobile_proxy=is_mobile_proxy,
                              is_data_center_proxy=is_data_center_proxy, is_home_proxy=is_home_proxy)
            db.session.add(new_proxy)
            db.session.commit()
            proxies += (new_proxy,)
        return proxies_schema.jsonify(proxies)
    else:
        all_proxies = Proxy.query.all()
        result = proxies_schema.dump(all_proxies)
        return jsonify(result.data)


def is_valid(proxy_type: str, host: str, port: str):
    proxy_dict = {proxy_type: host + ":" + port}
    test_site = {"http://www.google.com"}
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)'}

    for site in test_site:
        try:
            r = requests.get(site, headers=headers, proxies=proxy_dict)
            status = r.status_code
            if status is 200:
                return True
            else:
                return False
        except Exception as e:
            log("Exception: " + str(e))
            pass


def check_validity():
    for proxy in Proxy.query.all():
        proxy_id = proxy.id
        try:
            is_valid_proxy = is_valid(proxy_type=proxy.type, host=proxy.ip, port=proxy.port)
            if isinstance(is_valid_proxy, bool):
                db.session.query(Proxy).filter(Proxy.id == proxy_id).update({Proxy.is_valid: is_valid_proxy})
                db.session.commit()
        except Exception as e:
            log("Error while checking validity: " + str(e))
            pass
    log("Checked validity")


if __name__ == '__main__':
    db.create_all()
    check_validity()
    app.run(debug=True)
