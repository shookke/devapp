from app import app, db
from app.models import User, Container

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Container': Container}

#app.run(host='0.0.0.0', port=80)