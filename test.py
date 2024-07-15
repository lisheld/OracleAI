from vars import base_params,base_url
from newhelpers import get_endpoint
print(get_endpoint(f'{base_url}/sports', params = base_params|{'all':'true'}))