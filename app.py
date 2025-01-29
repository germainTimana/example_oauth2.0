from flask import Flask, request, jsonify, redirect, url_for
from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.oauth2.rfc6749.grants import AuthorizationCodeGrant
from models import CLIENTS, USERS
from authlib.oauth2.rfc6749 import ClientMixin
import os


# Permitir HTTP en entorno de desarrollo
os.environ["AUTHLIB_INSECURE_TRANSPORT"] = "1"

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Tu clase de cliente (debe implementar ClientMixin)
class OAuth2Client(ClientMixin):
   def __init__(self, client_id, client_secret, redirect_uris):
      self.client_id = client_id
      self.client_secret = client_secret
      self.redirect_uris = redirect_uris
   
   def check_redirect_uri(self, redirect_uri):
      return redirect_uri in self.redirect_uris
      
   # Implementa check_response_type
   def check_response_type(self, response_type):
      # Este método debe validar los tipos de respuesta esperados. Para un flujo de código de autorización el tipo de respuesta esperado debe ser 'code'.
      if response_type == 'code':
         return True
      return False

# Base de datos simulada para los clientes (puedes usar una real)
clients = {
    "client_id_123": OAuth2Client(
        client_id="client_id_123",
        client_secret="client_secret_123",
        #redirect_uris=["http://localhost:5000/callback"],
        redirect_uris="http://localhost:5000/callback",
    )
}

# Función para obtener un cliente basado en client_id
def query_client(client_id):
   print(f"🔍 Buscando cliente con ID: {client_id}")  
   client = clients.get(client_id)
   if client is None:
      print(f"❌ Cliente con ID {client_id} no encontrado")
   else:
      print(f"✅ Cliente encontrado con ID {client_id} y redirect_uris: {client.redirect_uris}")
   return client

# Configurar el servidor de autorización
authorization = AuthorizationServer()

# Asignar directamente la función query_client al servidor
authorization.query_client = query_client

# Luego inicializas el servidor con tu aplicación Flask
authorization.init_app(app)

# Grant personalizado para manejar el flujo de código de autorización
class MyAuthorizationCodeGrant(AuthorizationCodeGrant):
   def authenticate_user(self, authorization_code):
      # Simulación de autenticación de usuario (puedes usar tu base de datos)
      return USERS.get("2")

# Registro del grant
authorization.register_grant(MyAuthorizationCodeGrant)

# Endpoint para manejar /authorize
@app.route("/authorize", methods=["GET", "POST"])
def authorize():
   if request.method == "GET":
      # Simulación de usuario autenticado
      user = USERS.get("2")
      if not user:
         return jsonify({"error": "User not authenticated"}), 403
      print(f"🔍 Usuario encontrado:")
      print(f"    ID: {user.user_id}")
      print(f"    Username: {user.username}")
      try:
         # Obtener el consent grant
         grant = authorization.get_consent_grant(end_user=user)
         # grant = ['AUTHORIZATION_CODE_LENGTH', 'ERROR_RESPONSE_FRAGMENT', 'GRANT_TYPE', 'RESPONSE_TYPES', 'TOKEN_ENDPOINT_AUTH_METHODS', 'TOKEN_ENDPOINT_HTTP_METHODS', 'TOKEN_RESPONSE_HEADER', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_hooks', 'authenticate_token_endpoint_client', 'authenticate_user', 'check_authorization_endpoint', 'check_token_endpoint', 'client', 'create_authorization_response', 'create_token_response', 'delete_authorization_code', 'execute_hook', 'generate_authorization_code', 'generate_token', 'prompt', 'query_authorization_code', 'redirect_uri', 'register_hook', 'request', 'save_authorization_code', 'save_token', 'server', 'validate_authorization_redirect_uri', 'validate_authorization_request', 'validate_consent_request', 'validate_no_multiple_request_parameter', 'validate_requested_scope', 'validate_token_request']

         ##imprimir grant
         #print(dir(grant))
         print(grant.save_token)
      except Exception as e:
         print(f"Error al obtener el grant: {str(e)}")
         return jsonify({"error": "Error processing consent"}), 500

      return jsonify({
         "client_id": grant.client.client_id,
         "redirect_uri": grant.redirect_uri,
         "scope": grant.request.scope,
         "State": grant.request.state
         })
   elif request.method == "POST":
      return authorization.create_authorization_response()

# Endpoint para manejar /token
@app.route("/token", methods=["POST"])
def issue_token():
    return authorization.create_token_response()

# Endpoint protegido (recurso)
@app.route("/protected", methods=["GET"])
def protected_resource():
   token = request.headers.get("Authorization")
   if token != "Bearer valid_token":
      return jsonify({"error": "Unauthorized"}), 401
   return jsonify({"message": "Welcome to the protected resource!"})

if __name__ == "__main__":
    app.run(debug=True)