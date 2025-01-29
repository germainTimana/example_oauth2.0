# models.py
class User:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username

# Base de datos simulada
USERS = {
    "1": User(user_id="1", username="test_user"),
    "2": User(user_id="2", username="user2")
}

class Client:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def check_redirect_uri(self, redirect_uri):
        return self.redirect_uri == redirect_uri

# Base de datos simulada de clientes
CLIENTS = {
    "client_id_123": Client(client_id="client_id_123", client_secret="secret_123", redirect_uri="http://localhost:5000/callback")
}