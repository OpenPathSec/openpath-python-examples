# pip install AWSIoTPythonSDK (https://github.com/aws/aws-iot-device-sdk-python#install-from-pip)
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import base64
import json
import sys
import time
import urllib3

def messageHandler(client, userdata, message):
    print('received message on topic', message.topic)
    payload = json.loads(message.payload.decode())
    print(json.dumps(payload, indent=2))
    print('----\n\n')

api_base = 'https://api.openpath.com'

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('usage: %s <username> <password> <org_id> <acu_id>' % sys.argv[0])
        sys.exit(1)
    username = sys.argv[1]
    password = sys.argv[2]
    org_id = sys.argv[3]
    acu_id = sys.argv[4]
    if len(sys.argv) > 5:
        api_base = sys.argv[5]

    print('hello')

    op_auth = 'Basic %s' % base64.b64encode(('%s:%s' % (username, password)).encode()).decode()
    print('built auth string')

    sess = urllib3.PoolManager()
    r = sess.request('GET', '%s/orgs/%s/mqttCredentials?options=withShadows' % (api_base, org_id), headers={
        'Authorization': op_auth
    })
    creds = json.loads(r.data.decode())['data']
    # print(json.dumps(creds, indent=2))
    print('fetched credentials')

    client = AWSIoTMQTTClient(creds['clientId'], useWebsocket=True)
    print('created client')

    client.configureEndpoint(creds['atsEndpoint'], 443)
    print('configured endpoint')

    client.configureCredentials('./AmazonRootCA1.pem')
    print('configured root CA')

    client.configureIAMCredentials(creds['accessKeyId'], creds['secretAccessKey'], creds['sessionToken'])
    print('configured IAM credentials')

    client.connect()
    print('connected')

    for topic in creds['subscribeTopics']:
        client.subscribe(topic, 1, messageHandler)
        print('subscribed', topic)


    r = sess.request('POST', '%s/orgs/%s/acus/%s/refreshShadow' % (api_base, org_id, acu_id), headers={
        'Authorization': op_auth
    })
    print('requested shadow refresh')

    while True:
        print('sleeping...')
        time.sleep(1)
