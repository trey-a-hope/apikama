# Utility functions for handling server configuration and authentication
# Author: Trey Hope
# Created: December 2024

import base64
from models.client_config import ClientConfig
from urllib.parse import unquote


def buildClientConfig(server_string: str) -> ClientConfig:
   """
   Builds a ClientConfig object from an encoded server string.
   
   Args:
       server_string: URL-encoded string containing server connection details
       
   Returns:
       ClientConfig object with decoded server connection parameters
   """
   decoded_string: str = unquote(server_string)
   return _decode_server_string(decoded_string)


def encode_auth(auth_string: str) -> str:
   """
   Encodes an authentication string to base64 for use in Authorization headers.
   
   Args:
       auth_string: String to encode (typically in format "serverKey:")
       
   Returns:
       Base64 encoded string for use in Authorization header
   """
   auth_bytes: bytes = auth_string.encode("utf-8")
   return base64.b64encode(auth_bytes).decode("utf-8")


def get_base_url(host: str, ssl: bool, http_port: int) -> str:
   """
   Constructs the base URL for the Nakama server API.
   
   Args:
       host: Server hostname or IP address
       ssl: Whether to use HTTPS protocol
       http_port: Port number for HTTP/HTTPS connections
       
   Returns:
       Complete base URL string including protocol, host, port and API version
   """
   protocol: str = "https" if ssl else "http"
   return f"{protocol}://{host}:{http_port}/v2/"


def _decode_server_string(server_str: str) -> ClientConfig:
   """
   Decodes a server string into its component parts and creates a ClientConfig.
   
   Format: host:port:ssl:key
   Example: "127.0.0.1:7350:0:defaultkey"
   
   Args:
       server_str: Colon-separated string containing server configuration
       
   Returns:
       ClientConfig object with parsed server parameters
       
   Note:
       SSL is encoded as "1" for true, "0" for false
   """
   host, port, ssl, key = server_str.split(":")
   return ClientConfig(
       host=host,
       ssl=ssl == "1",
       serverKey=key,  # TODO: Make this more secretive...
       httpPort=int(port),
   )