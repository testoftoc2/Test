from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from cachetools import TTLCache
import app.utils.jwt_token as jwt_token
import json
import asyncio

app = Flask(__name__)
CORS(app)


cache = TTLCache(maxsize=100, ttl=300)

def cached_endpoint(ttl=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = (request.path, tuple(request.args.items()))
            if cache_key in cache:
                return cache[cache_key]
            else:
                result = func(*args, **kwargs)
                cache[cache_key] = result
                return result
        return wrapper
    return decorator




@app.route('/info')
@cached_endpoint()
def get_account_info():
    region = request.args.get('region')
    uid = request.args.get('uid')
    
    if not uid:
        response = {
            "error": "Invalid request",
            "message": "Empty 'uid' parameter. Please provide a valid 'uid'."
        }
        return jsonify(response), 400, {'Content-Type': 'application/json; charset=utf-8'}

    if not region:
        response = {
            "error": "Invalid request",
            "message": "Empty 'region' parameter. Please provide a valid 'region'."
        }
        return jsonify(response), 400, {'Content-Type': 'application/json; charset=utf-8'}

    return_data = asyncio.run(jwt_token.GetAccountInformation(uid, "7", region, "/GetPlayerPersonalShow"))
    formatted_json = json.dumps(return_data, indent=2, ensure_ascii=False)
    return formatted_json, 200, {'Content-Type': 'application/json; charset=utf-8'}


if __name__ == '__main__':
    app.run(port=3000, host='0.0.0.0', debug=True)