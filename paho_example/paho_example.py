import base64
import json
import logging
import ssl
import sys
import time
import urllib3
from threading import Event

import paho.mqtt.client as mqtt

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

    print('websocketsUrl', creds['websocketsUrl'])

    clean_session = True
    use_wss = True
    protocol = mqtt.MQTTv311
    user_data = None
    paho_client = mqtt.Client(creds['clientId'], clean_session, user_data, protocol, 'websockets')
    print('created paho client')

    def on_disconnect(client, user_data, rc):
        print('handling [disconnect] event')
        sys.exit(1)

    def on_message(client, user_data, message):
        print('handling [message] event')
        print('received message on topic', message.topic)
        payload = json.loads(message.payload.decode())
        print(json.dumps(payload, indent=2))
        print('----\n\n')

    def on_log(client, userdata, level, buf):
        print('[log]', userdata, level, buf)
    paho_client.on_log = on_log
    paho_client.on_disconnect = on_disconnect
    paho_client.on_message = on_message

    print('set up callbacks')

    ca_path = './AmazonRootCA1.pem'
    paho_client.tls_set(ca_certs=ca_path, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_SSLv23)
    print('configured root CA')

    host = creds['atsEndpoint']
    port = 443

    path_parts = creds['websocketsUrl'].split('/', 4)
    path = '/' + path_parts[3]
    paho_client.ws_set_options(path=path, headers={
        # override in order to explicitly NOT send the port number
        'Host': host
    })
    print('configured websockets path and headers')

    ## connect
    event = Event()
    def on_connect(client, user_data, flags, rc):
        print('handling [connack] event')
        event.set()

    paho_client.on_connect = on_connect
    keep_alive_seconds = 600
    rc = paho_client.connect(host, port, keep_alive_seconds)
    if mqtt.MQTT_ERR_SUCCESS == rc:
        print('starting network I/O thread...')
        paho_client.loop_start()
    else:
        print('connect error: %d' % rc)
        sys.exit(1)

    if not event.wait(10):
        print('connect timed out')
        sys.exit(1)
    print('connected')

    ## subscribe
    qos = 1
    for topic in creds['subscribeTopics']:
        event = Event()
        def on_subscribe(client, user_data, mid, granted_qos):
            print('handling [suback] event')
            event.set()
        paho_client.on_subscribe = on_subscribe
        rc, mid = paho_client.subscribe(topic, qos)
        if mqtt.MQTT_ERR_SUCCESS != rc:
            print('subscribe error: %d' % rc)
            sys.exit(1)
        if not event.wait(10):
            print('subscribe timed out')
            sys.exit(1)
        print('subscribed', topic)

    ## publish
    if False:
        rc, mid = paho_client.publish(topic, payload, qos, retain)

    r = sess.request('POST', '%s/orgs/%s/acus/%s/refreshShadow' % (api_base, org_id, acu_id), headers={
        'Authorization': op_auth
    })
    print('requested shadow refresh')

    while True:
        print('sleeping...')
        time.sleep(1)
