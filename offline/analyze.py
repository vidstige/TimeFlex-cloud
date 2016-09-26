from __future__ import print_function
import json

def stripx(s, suffix):
    if s.endswith(suffix):
        return s[:-len(suffix)]
    return s

with open('scans.html') as f:
    checked_in = False
    for line in f:
        scan = json.loads(stripx(line.rstrip(), '<br>'))
        scan.pop('_id')
        time = scan['time']
        ssids = [ap['ssid'] for ap in scan['access_points']]
        
        if u'Volumental' in ssids:
            if not checked_in:
                print('IN:  {}'.format(time))
            checked_in = True
        else:
            if checked_in:
                print('OUT: {}'.format(time))
            checked_in = False