import os
import json
import ipfshttpclient
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# NFT Metadata
ipfs_api = ipfshttpclient.connect('/ip4/<IPFS_SERVER>/tcp/5001')
metadata = {}

with open('metadata.json', 'r', encoding='utf-8') as metadata_template:
    metadata = json.load(metadata_template)

def minter(filename, prompt):
    res = ipfs_api.add(filename)
    hash = res['Hash']
    image_url = 'https://ipfs.io/ipfs/' + hash
    metadata["image"]=image_url
    metadata["name"]= prompt
    metadata["attributes"][0]["value"] = prompt

    nft_directory = 'minted/'
    metadata_filename = nft_directory+hash+'_metadata.json' 
    with open(metadata_filename, 'w', encoding='utf-8') as metadata_file:
        json.dump(metadata, metadata_file)

    metadata_res = ipfs_api.add(metadata_filename)
    metadata_CID = metadata_res['Hash']
    print(metadata_res)
    return metadata_CID

# Routes
@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")

# sanity check route
@app.route('/status', methods=['GET'])
def ping_pong():
    return jsonify('Ok')

# Application routes
@app.route('/generate', methods=['POST'])
def generate_image():
    prompt = request.form["prompt"]
    filename = prompt[:64].replace(' ', '_')+'.jpg'
    prompt_string = f"--text=\"{prompt}\" --grid-size=2 --no-mega --seed=-1 --image-path=static/generated/{filename}"
    os.system(f"py DreemDalle/image_from_text.py {prompt_string}")
    generated_image = {
            "prompt": prompt,
            "filename": filename
    }
    return  jsonify(generated_image)

@app.route('/mint', methods = ['POST'])
def mint():
    if request.method == 'POST':
        filename = request.form['filename']
        prompt = request.form['prompt']
        print("Minting" + filename)
        print("Generating metadata and uploading to IPFS")
        minter('static/generated/'+filename, prompt)

        print(filename)

        return(filename)

    
if __name__ == '__main__':
    app.run(host='0.0.0.0')