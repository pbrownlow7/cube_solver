from flask import Flask, jsonify, request
from flask_cors import CORS
from cube import *
import json

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def hello():
    c = Cube()
    s = CreateScramble()
    nice_s = listToStr(s)
    for r in s:
        c.RotateWithNotation(r)
    cube_list = squaresToList(c._cube)
    return jsonify(nice_sc=nice_s, cube_snap=cube_list, sc=s)

@app.route("/solve", methods=["POST"])
def solve():
    scramble = request.get_json()
    m_and_s = SolveCubeWithScramble(scramble["scramble"])
    return jsonify(mov=m_and_s[0], snaps=m_and_s[1])

if __name__ == '__main__':
    app.run()
