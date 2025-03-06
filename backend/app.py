from flask import Flask
from auth_routes import auth_blueprint
from leaderboard_routes import leaderboard_blueprint
from chat_routes import chat_blueprint
from game_routes import game_blueprint

app = Flask(__name__)

# Register blueprints
app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(leaderboard_blueprint, url_prefix="/leaderboard")
app.register_blueprint(chat_blueprint, url_prefix="/chat")
app.register_blueprint(game_blueprint, url_prefix="/game")

if __name__ == "__main__":
    app.run(debug=True)
