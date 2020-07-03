from waitress import serve

from rest.root import app

serve(app, host='0.0.0.0', port=80)
