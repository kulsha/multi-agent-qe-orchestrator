import sys
sys.path.append('.')
from config.llm_config import get_client

client = get_client('claude')
print('Claude client created successfully')