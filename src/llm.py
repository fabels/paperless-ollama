import ollama
from config import Config

client = ollama.Client(host=Config.OLLAMA_HOST)

generate = client.generate
embed = client.embed