import streamlit as st
import os
from openai import OpenAI
from streamlit_option_menu import option_menu
from datetime import datetime
import pandas as pd
from io import BytesIO
import requests
import base64
from gtts import gTTS
import pygame

@st.cache_resource
def initialization_function():
  answers = pd.DataFrame(columns = ['Model', 'Question', 'Answer'])
  return answers

@st.cache_resource
def initialization_function2():
  gallery = []
  return gallery
    
answers = initialization_function()
gallery = initialization_function2()

mp3_fp = BytesIO()

st.set_page_config(
  layout = 'wide',
  page_title = 'Ask AI with Python',
  page_icon = 'ikon.png', # https://map.ksh.hu/timea/images/shortcut.ico
  menu_items = {'Get help': 'mailto:adam.szilagyi@ksh.hu',
                'Report a bug': 'mailto:adam.szilagyi@ksh.hu',
                'About': 'This webapplication makes you able to chat and generate picture with ChatGPT through OpenAI module.'}
  )
  
st.title('Ask AI with Py')

selected = option_menu(None, ['Chat', 'Image', 'Galery'], menu_icon = 'cast', default_index = 0, orientation = 'horizontal')

if selected == 'Chat': 
  
  password = st.text_input('Set your OpenAI API key:', type = 'password', value = os.environ['OPENAI_API_KEY'], placeholder = "If you don't have one, then you can create here: https://platform.openai.com/api-keys")
  model = st.selectbox('Choose AI Model:', options = ['gpt-5.2', 'gpt-5', 'gpt-5-mini', 'gpt-5-nano'])
  question = st.text_area('Write here your question:', placeholder = 'Ask something!', value = None) # question = st.chat_input(placeholder = 'Write here your question:') 
  
  if st.button('Answer me!'): 
    try:
      with st.spinner('In progress...'):
        client = OpenAI(api_key = password)
        model = model # os.environ['OPENAI_MODEL']
        response = client.chat.completions.create(model = model, messages = [{"role": "system", "content": "You are a beautiful girl."}, {"role": "user", "content": question}], temperature = 0)
        answer = response.choices[0].message.content.strip()
        st.text(answer) # message = st.chat_message('ai')
        # message.write(answer)
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = 'Chat' + now + '.txt'
        answers.loc[len(answers)] = [model, question, answer]
        
        # response = client.chat.completions.create(
        #   model = model,
        #   messages = [
        #     {"role": "system", "content": "You are a language detection assistant. Return only the ISO 639-1 language code (e.g., 'en', 'es', 'fr') for the provided text. Do not provide any other text."},
        #     {"role": "user", "content": question}
        #   ],
        #   temperature = 0 # Low temperature for consistent, factual results
        # )
        # language = response.choices[0].message.content.strip()
        # 
        # tts = gTTS(text = answer, lang = language) # , lang = 'en' # answers['Answer'].iloc[-1]
        # tts.write_to_fp(mp3_fp)
        # 
        # mp3_fp.seek(0)
        # 
        # pygame.mixer.init()
        # pygame.mixer.music.load(mp3_fp, 'mp3')
        # pygame.mixer.music.play()
        
        st.download_button(label = 'Download Chat', data = answers.to_csv(index = False).encode('utf-8'), file_name = filename) # ';'.join([model, mquestion, answer])
    except Exception as e:
      st.error(f'An Error happened: {e}')
  
elif selected == 'Image':
  
  password2 = st.text_input('Set your OpenAI API key:', type = 'password', value = os.environ['OPENAI_API_KEY'], placeholder = "If you don't have one, then you can create here: https://platform.openai.com/api-keys")
  model2 = st.selectbox('Choose AI Model:', options = ['dall-e-3', 'chatgpt-image-latest', 'gpt-image-1.5', 'gpt-image-1', 'gpt-image-1-mini']) #  'gpt-image-1', 'gpt-image-1-mini', 'gpt-image-1.5', 'chatgpt-image-latest', 'dall-e-2', and 'dall-e-3'.
  desciption = st.text_area('What should the picture depict?', placeholder = 'Describe here...')
  if st.button('Draw me!'):
    try:
      with st.spinner('In progress...'):
        client = OpenAI(api_key = password2)
        response = client.images.generate(
          model = model2, 
          prompt = desciption, 
        )
          
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = 'image' + now + '.png'
        
        if model2 == 'dall-e-3':
          link = response.data[0].url
          r = requests.get(link)
          image_bytes = BytesIO(r.content)
          gallery.append(image_bytes) # link
        else:
          image_base64 = response.data[0].b64_json
          image_bytes = base64.b64decode(image_base64)
          gallery.append(image_bytes)
          
        left_co, cent_co,last_co = st.columns(3)
        with cent_co:
          st.image(image_bytes) # link
          st.download_button(label = 'Download Image',
                            data = image_bytes, # BytesIO(r.content)
                            file_name = filename,
                            mime = 'image/png')
          
    except Exception as e:
      st.error(f'An Error happened: {e}')
  
elif selected == 'Galery':
  
  left_co, cent_co,last_co = st.columns(3)
  with cent_co:
  
    if len(gallery) == 1:
      st.image(gallery[0])
      
      now = datetime.now().strftime('%Y%m%d%H%M%S')
      filename = 'image' + now + '.png'
      # r = requests.get(gallery[0])
      st.download_button(label = 'Download Image',
                          data = gallery[0], # BytesIO(r.content),
                          file_name = filename,
                          mime = 'image/png')
                          
    elif len(gallery) > 1:
      PictureRow = st.slider('Choose picture from your actual online gallery:', 0, len(gallery) - 1, 0)
      st.image(gallery[PictureRow])
      
      now = datetime.now().strftime('%Y%m%d%H%M%S')
      filename = 'image' + now + '.png'
      # r = requests.get(gallery[PictureRow])
      st.download_button(label = 'Download Image',
                          data = gallery[PictureRow], # BytesIO(r.content),
                          file_name = filename,
                          mime = 'image/png')
  
    else:
      st.success("You didn't make any image in this online session still.")
