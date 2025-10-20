from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "API is working!"})


@app.route("/get_data", methods=["GET"])
def get_data():
    return jsonify(
        {
            "A": "Data 1",
            "B": "Data 2",
            "C": "Data 3",
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
