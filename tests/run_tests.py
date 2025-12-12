import os, sys
# Ensure project root is on sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.utils.hash_utils import HashUtils
from app.utils.jwt_utils import JWTUtils
from datetime import timedelta
import sys


def run():
    try:
        print('Running hash utils test...')
        pw = 'myS3cret!'
        hashed = HashUtils.hash_password(pw)
        assert hashed != pw
        assert HashUtils.verify_password(pw, hashed)
        assert not HashUtils.verify_password('wrong', hashed)
        print('Hash utils test passed')

        print('Running JWT utils test...')
        payload = {'admin_id': 'testid', 'email': 'a@b.com', 'organization_name': 'org1'}
        token = JWTUtils.create_access_token(payload, expires_delta=timedelta(seconds=60))
        assert isinstance(token, str) and len(token) > 0
        decoded = JWTUtils.decode_access_token(token)
        assert decoded.admin_id == payload['admin_id']
        assert decoded.email == payload['email']
        assert decoded.organization_name == payload['organization_name']
        print('JWT utils test passed')

    except AssertionError as e:
        print('TEST FAILED:', e)
        sys.exit(1)
    except Exception as exc:
        print('ERROR during tests:', exc)
        sys.exit(2)

    print('All tests passed')

if __name__ == '__main__':
    run()
