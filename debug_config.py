import sys
sys.path.append('.')
from config.llm_config import get_client, PROVIDERS

print('=== PROVIDERS KEYS ===')
for k in PROVIDERS:
    model = PROVIDERS[k]['model']
    base_url = PROVIDERS[k].get('base_url', 'DEFAULT-OPENAI')
    print(f'{k}: model={model} base_url={base_url}')

print()
print('=== TESTING get_client groq ===')
client = get_client(provider='groq')
print('groq client created successfully')

print()
print('=== TESTING get_client ollama ===')
client2 = get_client(provider='ollama')
print('ollama client created successfully')