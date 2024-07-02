from helpers import get_endpoint

base_url = 'https://api.the-odds-api.com/v4'
base_params = {'apiKey': "ca938397d0849ca624c7d0043fd62b91"}   
sports = get_endpoint(f"{base_url}/sports", params = base_params|{'all':'true'})
print({sport['key']: ['outrights'] if sport['has_outrights'] else ['h2h','spreads','totals'] for sport in sports})
