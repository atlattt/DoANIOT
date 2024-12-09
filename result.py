import execjs
import re
import joblib
import numpy as np
from scipy.sparse import csr_matrix
from tensorflow.keras.models import load_model
import sys
from sklearn.preprocessing import StandardScaler,MaxAbsScaler,MinMaxScaler
import GetAllJSInPage
sys.stdout.reconfigure(encoding='utf-8')
#-1 benign 1 malicious
# List of features to count as per the table
features = {
    'eval()': r'\beval\(',
    'setTimeout()': r'\bsetTimeout\(',
    'iframe': r'iframe',
    'unescape()': r'\bunescape\(',
    'escape()': r'\bescape\(',
    'classid': r'classid',
    'parseInt()': r'\bparseInt\(',
    'fromCharCode()': r'\bfromCharCode\(',
    'ActiveXObject()': r'\bActiveXObject\(',
    'string direct assignments': r'=[\s]*["\'].*["\']',
    'concat()': r'\bconcat\(',
    'indexOf()': r'\bindexOf\(',
    'substring()': r'\bsubstring\(',
    'replace()': r'\breplace\(',
    'document.addEventListener()': r'document\.addEventListener\(',
    'attachEvent()': r'\battachEvent\(',
    'createElement()': r'\bcreateElement\(',
    'getElementById()': r'getElementById\(',
    'document.write()': r'document\.write\(',
    'JavaScript word count': r'\b\w+\b',
    'JavaScript Keywords': r'\b(var|let|const|function|if|else|for|while|return|switch|case|break|continue|try|catch|finally|throw)\b',
    'No. of characters in JavaScript': r'.',
    'The ratio between keywords and words': '',
    'Entropy of JavaScript': '',
    'Length of Longest JavaScript Word': '',#*
    'The No. of Long Strings >200': r'["\'][^"\']{200,}["\']', 
    'Length of shortest JavaScript Word': '',     #*              
    'Entropy of the Longest JavaScript Word': '',
    'No. of Blank Spaces': r'\s', 
    'Average Length of Words': '', #*
    'No. Hex Values': r'0x[0-9a-fA-F]+',
    'Share of space characters': '', #*
    'search()': r'\bsearch\(',
    'split()': r'\bsplit\(',
    'onbeforeunload': r'\bonbeforeunload\b',
    'onload': r'\bonload\b',
    'onerror()': r'\bonerror\(',
    'onunload': r'\bonunload\b',
    'onbeforeload': r'\bonbeforeload\b',
    'onmouseover': r'\bonmouseover\b',
    'dispatchEvent': r'\bdispatchEvent\(',
    'fireEvent': r'\bfireEvent\(',
    'setAttribute()': r'\bsetAttribute\(',
    'window.location': r'\bwindow\.location\b',
    'charAt()': r'\bcharAt\(',
    'console.log()': r'\bconsole\.log\(',
    '.js files': r'\.js["\']',
    '.php files': r'\.php["\']',
    'var keyword': r'\bvar\b',
    'function keyword': r'\bfunction\b',
    'Math.random()': r'\bMath\.random\(',
    'charCodeAt()': r'\bcharCodeAt\(',
    'WScript': r'\bWScript\b',
    'decode()': r'\bdecode\(',
    'toString()': r'\btoString\(',
    'No. of Digits': r'\d',
    'No. of Encoded Characters': r'%[0-9A-Fa-f]{2}',
    'No. of Backslash Characters': r'\\',
    'No. of Pipe Characters': r'\|',
    'No. of % Characters': r'%',
    'No. of ( Characters': r'\(',
    'No. of ) Characters': r'\)',
    'No. of , Characters': r',',
    'No. of # Characters': r'\#',
    'No. of + Characters': r'\+',
    'No. of . Characters': r'\.',
    "No. of ' Characters": r"'",
    'No. of [ Characters': r'\[',
    'No. of ] Characters': r'\]',
    'No. of { Characters': r'\{',
    'No. of } Characters': r'\}',
    'Share of Encoded Characters': '',
    'Share of Digits Characters': '',
    'Share of Hex/Octal Characters': '',
    'Share of Backslash Characters': '',
    'Share of | Characters': '',
    'Share of % Characters': '',
}

# Sample JavaScript code (user-provided)
#Đưa vào địa chỉ trang web cần phân tích
# javascript_code = GetAllJSInPage.get_all_js_in_page('https://uis.ptithcm.edu.vn/#/home')

# Initialize a dictionary to store the counts
feature_counts = {}

# Function to calculate entropy
def calculate_entropy(text):
    from collections import Counter
    import math

    # Count frequency of each character
    frequency = Counter(text)
    text_length = len(text)

    # Calculate entropy
    entropy = -sum((freq / text_length) * math.log2(freq / text_length) for freq in frequency.values())
    return entropy

# Analyze the JavaScript code
def analyze_javascript_code(javascript_code):
    for feature, pattern in features.items():
        if pattern and feature != 'JavaScript word count':  # Nếu pattern có giá trị và không phải 'JavaScript word count'
            count = len(re.findall(pattern, javascript_code))
            feature_counts[feature] = count
        elif feature == 'JavaScript word count':
            words = re.findall(r'\b\w+\b', javascript_code)
            feature_counts['JavaScript word count'] = len(words)
            feature_counts['Average Length of Words'] = sum(len(word) for word in words) / len(words) if words else 0
            feature_counts['Length of Longest JavaScript Word'] = max(map(len, words)) if words else 0
            feature_counts['Length of shortest JavaScript Word'] = min(map(len, words)) if words else 0
        elif feature == 'The ratio between keywords and words':
            keywords_count = len(re.findall(features['JavaScript Keywords'], javascript_code))
            words_count = feature_counts['JavaScript word count']
            feature_counts[feature] = keywords_count / words_count if words_count else 0
        elif feature == 'Entropy of JavaScript':
            feature_counts[feature] = calculate_entropy(javascript_code)
        elif feature == 'Entropy of the Longest JavaScript Word':
            longest_word = max(re.findall(r'\b\w+\b', javascript_code), key=len, default="")
            feature_counts[feature] = calculate_entropy(longest_word)
        elif feature == 'The No. of Long Strings >200':
            long_strings = re.findall(r'["\'][^"\']{200,}["\']', javascript_code)
            feature_counts[feature] = len(long_strings)


    # Phần chia sẻ ký tự đặc biệt
    total_chars = feature_counts['No. of characters in JavaScript']

    # Tính các tỷ lệ ký tự đặc biệt
    feature_counts['Share of Encoded Characters'] = feature_counts['No. of Encoded Characters'] / total_chars if total_chars else 0
    feature_counts['Share of Digits Characters'] = feature_counts['No. of Digits'] / total_chars if total_chars else 0
    feature_counts['Share of Hex/Octal Characters'] = (len(re.findall(r'0x[0-9a-fA-F]+', javascript_code)) + len(re.findall(r'0[0-7]+', javascript_code))) / total_chars if total_chars else 0
    feature_counts['Share of Backslash Characters'] = feature_counts['No. of Backslash Characters'] / total_chars if total_chars else 0
    feature_counts['Share of | Characters'] = feature_counts['No. of Pipe Characters'] / total_chars if total_chars else 0
    feature_counts['Share of % Characters'] = feature_counts['No. of % Characters'] / total_chars if total_chars else 0
    feature_counts['Share of space characters'] = feature_counts['No. of Blank Spaces'] / total_chars if total_chars else 0
    # Filter data to include only entries with values greater than 0
    filtered_data = {index: value for index, (key, value) in enumerate(feature_counts.items()) if value > 0}
    return filtered_data

def change_data(data):
    for index, value in data.items():
        full_values[index] = value
    # Convert the data to a sparse matrix
    X = csr_matrix(full_values)
    #print(X)
    return X

def predict_with_SVM_model(data):
    model = joblib.load('js_malware_classifier.pkl')
    scaler = joblib.load('scaler.joblib')
    data = scaler.transform(data)
    #print(data)
    pred=model.predict(data)
    prob=model.predict_proba(data).max()*100
    print(pred)
    print(prob)
    if pred==1 :
        return ("Malicious",prob)
    else: return ("Benign",prob)

def predict_with_DENSE_CNN(data):
    scaler=joblib.load('scaler_Dense.joblib')
    data=scaler.transform(data)
    #print(data)
    model= load_model('js_malware_classifier_nn.h5')
    pred=model.predict(data)
    print(pred)
    if pred > 0.5:
        
        return'Malicious'
    else:
        
        return'Benign'


# Analyze the JavaScript code
# filtered_data = analyze_javascript_code(javascript_code)

# Function to change data to the format that the model can predict
full_values = np.full(len(features), 0)

# X = change_data(filtered_data)
# # Load the model
# print(predict_with_SVM_model(X))
# print(predict_with_DENSE_CNN(X))

