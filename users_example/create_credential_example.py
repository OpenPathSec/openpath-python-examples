import base64
import certifi
import json
import sys
import time
import urllib3

api_base = 'https://api.openpath.com'

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print('usage: %s <username> <password> <org_id> <user_email> <card_number>' % sys.argv[0])
        sys.exit(1)
    username = sys.argv[1]
    password = sys.argv[2]
    org_id = sys.argv[3]
    user_email = sys.argv[4]
    card_number = sys.argv[5]
    if len(sys.argv) > 6:
        api_base = sys.argv[6]

    print('hello')

    op_auth = 'Basic %s' % base64.b64encode(('%s:%s' % (username, password)).encode()).decode()
    print('built auth string')

    sess = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where())

    all_users = []
    all_credentials = []

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

    print('looking for matching user...')
    matching_users = [u for u in all_users if u['identity']['email'] == user_email]
    if len(matching_users) > 1:
        print(matching_users)
        print('oops, multiple users matched - please use a unique email')
        sys.exit(1)
    if len(matching_users) == 1:
        user = matching_users[0]
        print('found one matching user:', json.dumps(user, indent=2))
    else:
        print('no existing user matched; creating')
        first_name = 'Example'
        last_name = 'Doe'
        r = sess.request('POST', '%s/orgs/%s/users' % (api_base, org_id), body=json.dumps({
            'identity': {
                'firstName': first_name,
                'lastName': last_name,
                'email': user_email,
            },
        }), headers={
            'Authorization': op_auth,
            'Content-Type': 'application/json'
        })
        resp = json.loads(r.data.decode())
        user = resp['data']
        print('created a new user for %s:' % user_email, json.dumps(user, indent=2))

    matching_credentials = [c for c in all_credentials if c['user']['id'] == user['id'] and c['credentialType']['modelName'] == 'card' and c['card']['number'] == card_number]
    if len(matching_credentials) > 0:
        print('matching credential(s) already exist:', json.dumps(matching_credentials, indent=2))
    else:
        print('creating a new credential...')
        r = sess.request('POST', '%s/orgs/%s/users/%s/credentials' % (api_base, org_id, user['id']), body=json.dumps({
            'credentialTypeId': 2, # 2 ==> "card"
            'card': {
                'number': card_number,
                'isOutputEnabled': True,
            },
        }), headers={
            'Authorization': op_auth,
            'Content-Type': 'application/json'
        })
        # print(r)
        resp = json.loads(r.data.decode())
        # print(resp)
        credential = resp['data']

        print('created a new credential for %s:' % user_email, json.dumps(credential, indent=2))
