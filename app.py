from flask import Flask


# Create the Flask application object.
# __name__ tells Flask where the current application module is located.
app = Flask(__name__)


@app.route("/")
def hello_world():
    """Return a simple message for the home page."""

    return "Hello, World!"


if __name__ == "__main__":
    # Start the development server only when app.py is executed directly.
    # debug=True reloads the server after code changes and shows useful
    # error information during development.
    app.run(host="0.0.0.0", port=4999, debug=True)