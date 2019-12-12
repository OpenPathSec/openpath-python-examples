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

    all_users = []

    offset = 0
    limit = 200
    while True:
        print('fetching users %s..%s' % (offset, offset+limit))
        r = sess.request('GET', '%s/orgs/%s/users?offset=%s&limit=%s' % (api_base, org_id, offset, limit), headers={
            'Authorization': op_auth
        })
        resp = json.loads(r.data.decode())
        users = resp['data']
        print('... got %d users' % len(users))
        all_users.extend(users)
        if len(users) < limit:
            break
        else:
            offset += limit

    print('got %d users in total' % len(all_users))
    print('user ids+emails follow:')
    for u in all_users:
        print(u['id'], u['identity']['email'])
