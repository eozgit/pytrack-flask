from waitress import serve

from rest.root import app
import api

print(api.time())

serve(app, host='0.0.0.0', port=80)
