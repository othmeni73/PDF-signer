from flask import Flask, render_template
from routes.sign import sign_blueprint

app = Flask(__name__)

# Register blueprints
app.register_blueprint(sign_blueprint)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
