from gtts import gTTS
from io import BytesIO
import pygame

mp3_fp = BytesIO()

response = client.chat.completions.create(
  model = model,
  messages = [
    {"role": "system", "content": "You are a language detection assistant. Return only the ISO 639-1 language code (e.g., 'en', 'es', 'fr') for the provided text. Do not provide any other text."},
    {"role": "user", "content": question}
    ],
    temperature = 0 # Low temperature for consistent, factual results
)
language = response.choices[0].message.content.strip()

tts = gTTS(text = answer, lang = language) # , lang = 'en' # answers['Answer'].iloc[-1]
tts.write_to_fp(mp3_fp)

mp3_fp.seek(0)

pygame.mixer.init()
pygame.mixer.music.load(mp3_fp, 'mp3')
pygame.mixer.music.play()
