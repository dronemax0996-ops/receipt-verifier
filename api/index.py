from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image
import io
import json
import os

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

@app.route('/api/verify', methods=['POST'])
def verify_receipt():
    try:
        if 'image' not in request.files:
            return jsonify({"status": "error", "message": "رەسىم ھۆججىتى يۈكلەنمىدى"}), 400
        
        file = request.files['image']
        expected_amount = request.form.get('expected_amount', '0')
        
        image = Image.open(io.BytesIO(file.read()))
        
        prompt = f"""
        بۇ تۆلەم تالونى سۈرىتىنى ئىنچىكە تەكشۈرۈپ، پەقەت تۆۋەندىكى شەكىلدىلا JSON قايتۇر:
        {{
          "is_valid_receipt": true ياكى false,
          "detected_amount": (تېپىلغان پۇل سانى ياكى 0),
          "currency": "(پۇل بىرلىكى، مەسىلەن USD, USDT, TRY, CNY)",
          "transaction_id": "(ئەگەر بار بولسا كود، بولمىسا null)",
          "is_matching": true ياكى false (سومما {expected_amount} گە دەل چۈشەمدۇ?),
          "reason": "(قىسقىچە ئۇيغۇرچە چۈشەندۈرۈش ياكى تەكشۈرۈش نەتىجىسى)"
        }}
        """
        
        response = model.generate_content(
            [prompt, image],
            generation_config={"response_mime_type": "application/json"}
        )
        
        result_data = json.loads(response.text)
        return jsonify({"status": "success", "data": result_data})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

app = app
