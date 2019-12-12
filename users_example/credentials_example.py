import base64
import certifi
import json
import sys
import time
import urllib3

api_base = 'https://api.openpath.com'

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('usage: %s <username> <password> <org_id>' % sys.argv[0])
        sys.exit(1)
    username = sys.argv[1]
    password = sys.argv[2]
    org_id = sys.argv[3]
    if len(sys.argv) > 4:
        api_base = sys.argv[4]

    print('hello')

    op_auth = 'Basic %s' % base64.b64encode(('%s:%s' % (username, password)).encode()).decode()
    print('built auth string')

    sess = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where())

    all_credentials = []

    offset = 0
    limit = 200
    while True:
        print('fetching credentials %s..%s' % (offset, offset+limit))
        r = sess.request('GET', '%s/orgs/%s/credentials?offset=%s&limit=%s' % (api_base, org_id, offset, limit), headers={
            'Authorization': op_auth
        })
        resp = json.loads(r.data.decode())
        credentials = resp['data']
        print('... got %d credentials' % len(credentials))
        all_credentials.extend(credentials)
        if len(credentials) < limit:
            break
        else:
            offset += limit

    print('got %d credentials in total' % len(all_credentials))
    print('credential details follow:')
    for c in all_credentials:
        details = c[c['credentialType']['modelName']]
        desc = details.get('name') or details.get('number')
        print('%-8d %-25s %-30s %s' % (c['id'], c['credentialType']['modelName'], desc, c['user']['identity']['email']))
