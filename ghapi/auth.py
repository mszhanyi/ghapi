# AUTOGENERATED! DO NOT EDIT! File to edit: 02_auth.ipynb (unless otherwise specified).

__all__ = ['Scope', 'scope_str', 'GhDeviceAuth', 'github_auth_device']

# Cell
from fastcore.utils import *
from fastcore.foundation import *
from .core import *

import webbrowser,time
from urllib.parse import parse_qs,urlsplit

# Cell
_scopes =(
    'repo','repo:status','repo_deployment','public_repo','repo:invite','security_events','admin:repo_hook','write:repo_hook',
    'read:repo_hook','admin:org','write:org','read:org','admin:public_key','write:public_key','read:public_key','admin:org_hook',
    'gist','notifications','user','read:user','user:email','user:follow','delete_repo','write:discussion','read:discussion',
    'write:packages','read:packages','delete:packages','admin:gpg_key','write:gpg_key','read:gpg_key','workflow'
)

# Cell
Scope = AttrDict({o.replace(':','_'):o for o in _scopes})

# Cell
def scope_str(*scopes)->str:
    "Convert `scopes` into a comma-separated string"
    return ','.join(str(o) for o in scopes if o)

# Cell
_def_clientid = '771f3c3af93face45f52'

# Cell
class GhDeviceAuth(GetAttrBase):
    "Get an oauth token using the GitHub API device flow"
    _attr="params"
    def __init__(self, client_id=_def_clientid, *scopes):
        url = 'https://github.com/login/device/code'
        self.client_id = client_id
        self.params = parse_qs(urlread(url, client_id=client_id, scope=scope_str(scopes)))

    def _getattr(self,v): return v[0]

# Cell
@patch
def url_docs(self:GhDeviceAuth)->str:
    "Default instructions on how to authenticate"
    return f"""First copy your one-time code: {self.user_code}
Then visit {self.verification_uri} in your browser, and paste the code when prompted."""

# Cell
@patch
def open_browser(self:GhDeviceAuth):
    "Open a web browser with the verification URL"
    webbrowser.open(self.verification_uri)

# Cell
@patch
def auth(self:GhDeviceAuth)->str:
    "Return token if authentication complete, or `None` otherwise"
    resp = parse_qs(urlread(
        'https://github.com/login/oauth/access_token',
        client_id=self.client_id, device_code=self.device_code,
        grant_type='urn:ietf:params:oauth:grant-type:device_code'))
    err = nested_idx(resp, 'error', 0)
    if err == 'authorization_pending': return None
    if err: raise Exception(resp['error_description'][0])
    return resp['access_token'][0]

# Cell
@patch
def wait(self:GhDeviceAuth, cb:callable=None, n_polls=9999)->str:
    "Wait up to `n_polls` times for authentication to complete, calling `cb` after each poll, if passed"
    interval = int(self.interval)+1
    res = None
    for i in range(n_polls):
        res = self.auth()
        if res: return res
        if cb: cb()
        time.sleep(interval)

# Cell
def github_auth_device(wb='', n_polls=9999):
    "Authenticate with GitHub, polling up to `n_polls` times to wait for completion"
    auth = GhDeviceAuth()
    print(f"First copy your one-time code: \x1b[33m{auth.user_code}\x1b[m")
    print(f"Then visit {auth.verification_uri} in your browser, and paste the code when prompted.")
    if not wb: wb = input("Shall we try to open the link for you? [y/n] ")
    if wb[0].lower()=='y': auth.open_browser()

    print("Waiting for authorization...", end='')
    token = auth.wait(lambda: print('.', end=''), n_polls=n_polls)
    if not token: return print('Authentication not complete!')
    print("Authenticated with GitHub")
    return token