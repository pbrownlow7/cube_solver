from flask import Flask, jsonify, request
from flask_cors import CORS
from cube import *
import json

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def hello():
    c = Cube()
    s = CreateScrambleForWebPage()
    nice_s = listToStr(s[0])
    for r in s[0]:
        c.RotateWithNotation(r)
    return jsonify(nice_sc=nice_s, sc=s, usable_sc=s[1])

@app.route("/solve", methods=["POST"])
def solve():
    scramble = request.get_json()
    m_and_ml = SolveCubeWithScramble(scramble["scramble"])
    return jsonify(mov=m_and_ml[0], moves_list=m_and_ml[1])

if __name__ == '__main__':
    app.run()
