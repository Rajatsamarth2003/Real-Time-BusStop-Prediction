from flask import Flask, render_template, send_from_directory

app = Flask(__name__, static_folder='static', template_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    print("📱 Mobile App running at http://localhost:3000")
    app.run(debug=True, host='0.0.0.0', port=3000)