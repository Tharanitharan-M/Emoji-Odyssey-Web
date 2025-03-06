from flask import Flask
from flask_cors import CORS
from auth_routes import auth_blueprint
from leaderboard_routes import leaderboard_blueprint

app = Flask(__name__)
CORS(app)

# Registering Blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(leaderboard_blueprint)

if __name__ == "__main__":
    app.run(debug=True)
