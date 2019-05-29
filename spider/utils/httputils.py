import email
import json
from io import StringIO
import os

def convertRawString2Headers(request_text):
    request_line, headers_alone = request_text.replace(' ','').split('\n', 1)
    message = email.message_from_string(headers_alone) #email.message_from_file(StringIO(headers_alone))
    headers = dict(message.items())
    return headers

def convertRawString2Json(request_text):
    # return eval(request_text.replace('null', 'None').replace('false', 'False').replace('true', 'True').replace('\t', '').replace('\r', '').replace('\n', '').replace('\r\n', ''))
    return json.loads(request_text)

def loadJsonValueByKey(json, key):
    if key in json:
        return json[key]
    else:
        return ''