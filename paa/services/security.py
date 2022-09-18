import hashlib


def hash_sha256(password):
	password = hashlib.sha256(password.encode())
	return password.hexdigest()
