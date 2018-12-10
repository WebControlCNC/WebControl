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

        if command == "TextMessage" or command == "Alert":
            data = dictionary
        else:
            data = json.dumps(dictionary)
        msg = json.dumps({"command": command, "message": message, "data": data})

        return super(UIQueue, self).put(msg)
