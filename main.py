from flask import Flask, request, jsonify
from flask_cors import CORS
import result
import GetAllJSInPage
import getalljsfileinpage
app = Flask(__name__)
CORS(app)

@app.route('/api/data', methods=['POST'])
def api():
    try:
        data=request.get_json()
        url=data['url']
        print(url)
        javascript_code=getalljsfileinpage.get_all_js_in_page(url)
        print(javascript_code)
        feature_counts=result.analyze_javascript_code(javascript_code)
        X=result.change_data(feature_counts)
        my_prediction = result.predict_with_DENSE_CNN(X)   
        return jsonify({'messenger': my_prediction}), 200
    except Exception as e:
        return jsonify({'error':str(e)})
    
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000)