#!/usr/bin/env python

from statsapi import endpoints
lbb = """
* """
lb = """
"""

for k, v in endpoints.ENDPOINTS.items():
    print(f"## Endpoint: `{k}`{lb}")
    print(f"### URL: `{v['url']}`{lb}")
    rp = [pk for pk, pv in v['path_params'].items() if pv['required'] and pk != 'ver']
    # print(f"### Required Path Parameters{lb}{rp}")
    rq = [' + '.join(q) for q in v['required_params'] if len(q) > 0]
    # print(f"### Required Query Parameters{lb}{rq}")
    rp.extend(rq)
    print(f"### Required Parameters{lb}* {lbb.join(rp) if len(rp) else '*None*'}{lb}")
    ap = list(v['path_params'].keys()) + (v['query_params'] if v['query_params'] != [[]] else [])
    print(f"### All Parameters{lb}* {lbb.join(ap)}{lb}")
    if v.get("note"):
        print(f"### Note{lb}{v['note']}{lb}")

    print(f"-----{lb}")
