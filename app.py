from flask import Flask, render_template, redirect, url_for, request, session, send_from_directory, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)
