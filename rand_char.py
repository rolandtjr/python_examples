import random

characters = ''
try:
    characters = ''.join([chr(random.choice([i for i in range(0x0, 0xD7FF + 1) if i < 0xD800 or i > 0xDFFF])) for _ in range(5000)])
except UnicodeEncodeError as e:
    print(f"Error encoding character: {e}")

print(characters)
