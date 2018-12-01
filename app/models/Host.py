from .. import db


class Host(db.Model):
    __tablename__ = 'ppe_host'
    host_id = db.Column("host_id", db.Integer, primary_key=True, autoincrement=True)
    internal_ip = db.Column("internal_ip", db.String(15), unique=False, nullable=False)
    external_ip = db.Column("external_ip", db.String(15), unique=False, nullable=False)
    host_name = db.Column("host_name", db.String(45), unique=False, nullable=False)
    zone_id = db.Column("zone_id", db.Integer, nullable=False)

    def __init__(self, internal_ip, external_ip, host_name, zone_id):
        self.internal_ip = internal_ip
        self.external_ip = external_ip
        self.host_name = host_name
        self.zone_id = zone_id

    def __repr__(self):
        return '<Host %r>' + self.host_id
