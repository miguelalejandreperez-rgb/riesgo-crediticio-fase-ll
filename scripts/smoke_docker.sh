#!/usr/bin/env bash
set -euo pipefail

URL="${1:-http://localhost:8000}"
python - "$URL" <<'PY'
import json
import sys
import urllib.request

url = sys.argv[1].rstrip('/')
with urllib.request.urlopen(url + '/api/health', timeout=15) as response:
    health = json.load(response)
assert health['estado'] == 'listo', health
payload = {
    'LIMIT_BAL': 20000,
    **{name: 0 for name in ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']},
    **{f'BILL_AMT{i}': 10000 for i in range(1, 7)},
    **{f'PAY_AMT{i}': 1000 for i in range(1, 7)},
}
request = urllib.request.Request(
    url + '/api/predecir',
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}, method='POST'
)
with urllib.request.urlopen(request, timeout=20) as response:
    prediction = json.load(response)
assert 0 <= prediction['puntaje_incumplimiento'] <= 1
assert prediction['alerta'] == (prediction['puntaje_incumplimiento'] >= prediction['umbral_alerta'])
print('OK: /api/health y /api/predecir con modelo real')
print('Respuesta:', prediction)
PY
