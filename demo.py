#!/usr/bin/python

from datetime import datetime, timedelta
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
import time
import json
import scrypt


def lambda_handler(event, context):

    start = datetime.utcnow()

    print("Start: " + start.isoformat())

    messageObj = {"created": start.isoformat()}
    message = json.dumps(messageObj)
    valid = True

    t1 = time.time()
    rng = Random.new().read
    t2 = time.time()
    dt2 = t2 - t1
    print(str(dt2) + "s to generate random data")

    RSAkey = RSA.generate(2048, rng)
    t3 = time.time()
    dt3 = t3 - t2
    print(str(dt3) + "s to generate key")

    pubkey = RSAkey.publickey()

    publicPem = pubkey.exportKey()

    rsapub = RSA.importKey(publicPem)

    scrypt.encrypt("a secret message", "password", maxtime=0.1)

    t4 = time.time()
    dt4 = t4 - t3
    print(str(dt4) + "s to export/import key")

    hash = SHA256.new(message).digest()
    t5 = time.time()
    dt5 = t5 - t4
    print(str(dt5) + "s to hash message")

    signature = RSAkey.sign(hash, rng)
    t6 = time.time()
    dt6 = t6 - t5
    print(str(dt6) + "s to sign message")

    valid = rsapub.verify(hash, signature)
    t7 = time.time()
    dt7 = t7 - t6
    print(str(dt7) + "s to verify message")

    if valid:
        print("Successfully validated message")

        messageObj = json.loads(message)

        created = datetime.strptime(messageObj["created"], "%Y-%m-%dT%H:%M:%S.%f")
        now = datetime.utcnow()

        if created > now:
            print("Created in the future!")
        else:
            createdDelta = now - created

            maxAge = timedelta(minutes=5)
            if maxAge < createdDelta:
                print("Token has expired!")
            else:
                print(str(createdDelta.total_seconds()))

    else:
        print("Failed to validate message")

    return {"body": "TEST", "verified": valid}


if __name__ == "__main__":
    lambda_handler(None, None)
