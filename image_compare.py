from flask import Flask, jsonify, request
from PIL import Image
from flask_pymongo import PyMongo, pymongo
import urllib.request
import io
import imagehash

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'database'
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/database' #Url MongoDB

mongo = PyMongo(app)

@app.route("/", methods=['POST'])
def image_compare():
    
    #input value
    value_url = request.form['url_image']
    value_mongo = request.form['hash_mongo']
    
    #Query to collection mongodb
    fr_politis = mongo.db.fr_politisi
    hash_mongo = fr_politis.find_one({'hash' : value_mongo})
    value1 = str(hash_mongo['hash'])
    
    # Header URL
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 5.1; rv:43.0) Gecko/20100101 Firefox/43.0')]
    urllib.request.install_opener(opener)
    resp = urllib.request.urlopen(value_url)
    
    #Read URL
    image_file = io.BytesIO(resp.read())
    
    #Hashing Image from URL
    image = Image.open(image_file)
    value_hash = imagehash.phash(image, hash_size=8)
    value2 = str(value_hash)
    
    distance = 0
    divider = 1024
    
    dec1 = int(value1, 16);
    dec2 = int(value2, 16);
    bin1 = bin(dec1)
    bin2 = bin(dec2)
    xor_bin = int(bin1, 2) ^ int(bin2, 2)
    distance = bin(xor_bin).count("1")
    divider = len(value1) * 4
        
    result =  1 - (distance / float(divider))
        
    hash_accuracy = {
        'accuracy': float(result)
    }
     
    return jsonify(hash_accuracy)
    
if __name__ == '__main__':
    app.run(debug=true)