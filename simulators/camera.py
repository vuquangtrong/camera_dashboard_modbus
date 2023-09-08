"""
Simulate NC200 camera web server
"""
import random
from flask import Flask, request, json
app = Flask(__name__)


@app.route('/getmsginfo', methods=['POST'])
def getmsginfo():
    # print(request.json)

    response = {
        'action': 'response',
        'cmdtype': request.json['cmdtype'],
        'retcode': 0,
        'retmsg': 'success.'
    }

    if response['cmdtype'] == 501:  # login
        response['message'] = {
            'token': 'AABBCCDDEEFF'
        }
    elif response['cmdtype'] == 521:  # get temperature at point
        response['message'] = {
            'value': random.randrange(20, 30)
        }

    # print(response)

    return json.dumps(response)


if __name__ == '__main__':
    app.run()
