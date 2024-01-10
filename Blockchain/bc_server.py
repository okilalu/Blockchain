import json
import sys
import time
import hashlib
import os

from uuid import uuid4

from flask import Flask
from flask.globals import request
from flask.json import jsonify

import requests
from urllib.parse import urlparse

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

class Block:
    def __init__(self, index, previous_hash, timestamp, data, nonce, hash, difficulty):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        self.hash = hash
        self.difficulty = difficulty

def calculate_hash(index, previous_hash, timestamp, data, nonce):
    data_str = json.dumps(data, sort_keys=True)
    input_str = f"{index}{previous_hash}{timestamp}{data_str}{nonce}"
    return hashlib.sha256(input_str.encode('utf-8')).hexdigest()

def create_genesis_block():
    nonce = 0
    timestamp = str(int(time.time() * 1000))
    hash_value = calculate_hash(0, "0", timestamp, "Genesis Block", nonce)
    return Block(0, "0", timestamp, "Genesis Block", nonce, hash_value)

blockchain = []
used_certificate_numbers = set()

def load_blockchain():
    try:
        with open("blockchain.json", "r") as file:
            data = file.read()
            global blockchain
            blockchain = json.loads(data)
    except FileNotFoundError:
        global blockchain
        blockchain = [create_genesis_block()]

def save_blockchain():
    try:
        with open("blockchain.json", "w") as file:
            json.dump(blockchain, file, indent=4)
    except Exception as e:
        print("Error saving blockchain:", e)

load_blockchain()

private_key = ""
public_key = ""

def generate_key_pair():
    global private_key, public_key
    key = RSA.generate(2048)
    private_key = key.export_key().decode('utf-8')
    public_key = key.publickey().export_key().decode('utf-8')
    return {"privateKey": private_key, "publicKey": public_key}

def mine_block(index, previous_hash, timestamp, data, difficulty):
    nonce = 0
    target_prefix = "0" * difficulty

    while True:
        nonce += 1
        hash_value = calculate_hash(index, previous_hash, timestamp, data, nonce)
        if hash_value.startswith(target_prefix):
            return {"nonce": nonce, "hash": hash_value}

def add_block(data):
    global private_key, public_key

    if data["number"] in used_certificate_numbers:
        print("Certificate number has been used.")
        return None

    previous_block = blockchain[-1]
    index = previous_block.index + 1
    timestamp = str(int(time.time() * 1000))

    start_mining_time = time.time()
    result = mine_block(index, previous_block.hash, timestamp, data, 4)
    nonce, hash_value = result["nonce"], result["hash"]
    end_mining_time = time.time()
    mining_time = int((end_mining_time - start_mining_time) * 1000)
    print(f"Mining time: {mining_time} ms")

    data_to_sign = json.dumps(data, sort_keys=True)

    key = RSA.import_key(private_key)
    h = SHA256.new(data_to_sign.encode('utf-8'))
    signature = pkcs1_15.new(key).sign(h)

    new_block = Block(index, previous_block.hash, timestamp, data, nonce, hash_value, 4)

    is_signature_valid = verify_signature(data_to_sign, public_key, signature)
    print("Is block valid?", is_signature_valid)

    if is_signature_valid:
        blockchain.append(new_block)
        used_certificate_numbers.add(data["number"])
        save_blockchain()
    else:
        print("Digital signature is not valid.")

    return new_block if is_signature_valid else None

def verify_signature(data, public_key, signature):
    try:
        key = RSA.import_key(public_key)
        h = SHA256.new(data.encode('utf-8'))
        pkcs1_15.new(key).verify(h, signature)
        return True
    except Exception as e:
        print("Error verifying signature:", e)
        return False

app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', "")
blockchain = Block()

# Routes 
@app.route('/blockchain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200

@app.route('/mine_block', methods=['GET'])
def mine_block():
    index = 1  # Replace with the actual index
    previous_hash = "previous_hash"  # Replace with the actual previous hash
    timestamp = str(int(time.time()))
    data = {"some_key": "some_value"}  # Replace with the actual data
    difficulty = 4  # Replace with the actual difficulty

    result = mine_block_logic(index, previous_hash, timestamp, data, difficulty)
    
    response = {
        'nonce': result["nonce"],
        'hash': result["hash"]
    }

    return jsonify(response), 200

def mine_block_logic(index, previous_hash, timestamp, data, difficulty):
    nonce = 0
    target_prefix = "0" * difficulty

    while True:
        nonce += 1
        hash_value = calculate_hash(index, previous_hash, timestamp, data, nonce)
        if hash_value.startswith(target_prefix):
            return {"nonce": nonce, "hash": hash_value}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(sys.argv[1]))
