from app.build import Build
from app.models import Container
from flask_login import current_user
from flask import jsonify
from app import app, db

def build_job(job,container):
    container = Container.query.get(int(container))
    action = Build(
        container.name,
        container.database,
        container.db_user,
        container.db_pw,
        container.url,
        container.prefix
        )
    queued = action.build(job, current_user.token)
    status = action.status(job, queued)
    container.status = status
    db.session.commit()
    return jsonify({'status':status})
