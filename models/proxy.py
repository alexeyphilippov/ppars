from datetime import datetime
from app import db


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

