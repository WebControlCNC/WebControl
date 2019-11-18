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
        '''
        This is an attempt to standardize on the communications format.  There's probably a fair amount of work that
        should go into updating this.  The concept is that there are three elements:
        :param command: The type/command of the message
        :param message: The actual message
        :param dictionary: Values/Arguments that accompany the message
        :return:
        Some times things don't come across correctly, particularly text messages from the controller.  need to work
        on this and document it better.
        All three of the elements get converted into a single json string for insertion into the queue
        '''
        #if command == "TextMessage" or command == "Alert":
        #    data = dictionary # these are text lines, so no need to jsonify
        #else:
        try:
            # convert the dictionary to a json
            data = json.dumps(dictionary)
        except Exception as e:
            print("####")
            print(e)
            print("####")

        # convert the command, message, and jsonified dictionary into a json
        msg = json.dumps({"command": command, "message": message, "data": data})

        # put in uiqueue
        return super(UIQueue, self).put(msg)
