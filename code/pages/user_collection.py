from flask import render_template, Blueprint, request, current_app


user_collection_ = Blueprint(
    'user_collection', __name__, template_folder='templates')


@user_collection_.route('/user_collection')
def user_collection():
    key = request.args.get('key')
    if key == None:
        return render_template('user_collection.html')
    else:
        mongo = current_app.config['mongo']
        collection = mongo.db.spotty_user_collection
        collection.insert_one({'track': key})
        return render_template('user_collection.html')
