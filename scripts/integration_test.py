import json
import time
import urllib.request
from urllib.error import HTTPError
from datetime import datetime

BASE = 'http://127.0.0.1:8000'


def post(path: str, payload: dict, token: str | None = None):
    url = BASE + path
    data = json.dumps(payload).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.getcode(), json.load(resp)
    except HTTPError as e:
        try:
            body = e.read().decode()
            return e.code, json.loads(body)
        except Exception:
            return e.code, {'error': str(e)}


def get(path: str, token: str | None = None):
    url = BASE + path
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, headers=headers, method='GET')
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.getcode(), json.load(resp)
    except HTTPError as e:
        try:
            body = e.read().decode()
            return e.code, json.loads(body)
        except Exception:
            return e.code, {'error': str(e)}


def put(path: str, payload: dict, token: str | None = None):
    url = BASE + path
    data = json.dumps(payload).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, data=data, headers=headers, method='PUT')
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.getcode(), json.load(resp)
    except HTTPError as e:
        try:
            body = e.read().decode()
            return e.code, json.loads(body)
        except Exception:
            return e.code, {'error': str(e)}


def delete(path: str, payload: dict | None = None, token: str | None = None):
    url = BASE + path
    data = None
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='DELETE')
    try:
        with urllib.request.urlopen(req) as resp:
            try:
                return resp.getcode(), json.load(resp)
            except Exception:
                return resp.getcode(), resp.read().decode()
    except HTTPError as e:
        try:
            body = e.read().decode()
            return e.code, json.loads(body)
        except Exception:
            return e.code, {'error': str(e)}


def run():
    ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    org = f'testorg_{ts}'
    org_new = f'{org}_renamed'
    email = f'admin+{ts}@example.com'
    password = 'TestPass123!'

    print('1) Create organization', org)
    code, resp = post('/org/create', {'organization_name': org, 'email': email, 'password': password})
    print('->', code, resp)
    if code not in (200, 201):
        print('Create failed, abort')
        return

    time.sleep(0.5)

    print('\n2) Login as admin')
    code, resp = post('/admin/login', {'email': email, 'password': password})
    print('->', code, resp)
    if code != 200:
        print('Login failed, abort')
        return
    token = resp.get('access_token')

    time.sleep(0.2)

    print('\n3) Get current admin (/admin/me)')
    code, resp = get('/admin/me', token)
    print('->', code, resp)

    print('\n4) Get organization metadata')
    code, resp = get(f'/org/get?organization_name={org}')
    print('->', code, resp)

    print(f'\n5) Update organization name to {org_new}')
    code, resp = put('/org/update', {'old_organization_name': org, 'new_organization_name': org_new, 'email': f'new+{ts}@example.com', 'password': 'NewPass!234'}, token)
    print('->', code, resp)

    print('\n6) Get new organization metadata')
    code, resp = get(f'/org/get?organization_name={org_new}')
    print('->', code, resp)

    # After updating org name/email/password we must re-login to obtain a token
    new_email = f'new+{ts}@example.com'
    new_password = 'NewPass!234'
    print('\n7) Re-login with new admin credentials')
    code, resp = post('/admin/login', {'email': new_email, 'password': new_password})
    print('->', code, resp)
    if code != 200:
        print('Re-login failed, aborting delete')
        return
    token = resp.get('access_token')

    print('\n8) Delete organization')
    code, resp = delete('/org/delete', {'organization_name': org_new}, token)
    print('->', code, resp)

    print('\n9) Verify deletion (should be 404)')
    code, resp = get(f'/org/get?organization_name={org_new}')
    print('->', code, resp)


if __name__ == '__main__':
    run()
