from app import app, db, Users

with app.app_context():
    Users.query.delete()
    db.session.commit()
    print("Tous les utilisateurs ont été supprimés")
