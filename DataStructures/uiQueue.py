"""

This module provides a simple addition to the Queue, which is that it logs
puts to the Queue immediately.

"""

from queue import Queue
import json


class UIQueue(Queue):
    def __init__(self):
        super(UIQueue, self).__init__()

    def put(self, command, message, dictionary):

        #if command == "TextMessage" or command == "Alert":
        #    data = dictionary # these are text lines, so no need to jsonify
        #else:
        try:
            data = json.dumps(dictionary)
        except Exception as e:
            print("####")
            print(e)
            print("####")

        msg = json.dumps({"command": command, "message": message, "data": data})

        return super(UIQueue, self).put(msg)
