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

    if response['cmdtype'] == 20:  # get cold hot spot tracking
        response['message'] = {
            'trace_flag': 1,
            'alarm_shake': 0,
            'record_delay': 10,
            'high_flag': 1,
            'low_flag': 1,
            'high_temp': 34.5,
            'low_temp': 12.3
        }
    elif response['cmdtype'] == 501:  # login
        if request.json["message"]["username"] == "admin":
            response['message'] = {
                'token': 'AABBCCDDEEFF'
            }
        else:
            response["retcode"] = 10004

    elif response['cmdtype'] == 520:  # get real time temperature
        response['message'] = {
            'global_min_temp': round(random.uniform(10, 20), 1),
            'global_avg_temp': round(random.uniform(20, 30), 1),
            'global_max_temp': round(random.uniform(30, 40), 1)
        }

    print(response)

    return json.dumps(response)


if __name__ == '__main__':
    app.run()
