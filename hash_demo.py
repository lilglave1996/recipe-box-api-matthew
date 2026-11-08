from werkzeug.security import generate_password_hash, check_password_hash

password = "soup123"

hash_value = generate_password_hash(password, method="pbkdf2:sha256")
print("Stored hash:", hash_value)

print("Correct candidate:", check_password_hash(hash_value, "soup123"))
print("Wrong candidate:", check_password_hash(hash_value, "soup124"))