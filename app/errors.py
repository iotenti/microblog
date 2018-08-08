from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500) #500 = could be db error
def internal_error(error):
    db.session.rollback()#rollback db so nothing gets messed up.
    return render_template('500.html'), 500