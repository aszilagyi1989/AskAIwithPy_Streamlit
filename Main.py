import streamlit as st
import os
from openai import OpenAI
from streamlit_option_menu import option_menu
from datetime import datetime
import urllib
import pandas as pd
from io import BytesIO
import requests

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

st.set_page_config(
  layout = 'wide',
  page_title = 'Ask AI with Python',
  page_icon = 'https://map.ksh.hu/timea/images/shortcut.ico',
  menu_items = {'Get help': 'mailto:adam.szilagyi@ksh.hu',
                'Report a bug': 'mailto:adam.szilagyi@ksh.hu',
                'About': 'This webapplication makes you able to chat and generate picture with ChatGPT through OpenAI module.'}
  )
  
st.title('Ask AI with Py')

selected = option_menu(None, ['Chat', 'Image', 'Galery'], menu_icon = 'cast', default_index = 0, orientation = 'horizontal')

if selected == 'Chat': 
  
  password = st.text_input('Set your OpenAI API key:', type = 'password', value = os.environ['OPENAI_API_KEY'], placeholder = "If you don't have one, then you can create here: https://platform.openai.com/api-keys")
  model = st.selectbox('Choose AI Model:', options = ['gpt-5', 'gpt-5-mini', 'gpt-5-nano'])
  question = st.text_area('Write here your question:', placeholder = 'Ask something!', value = None) # question = st.chat_input(placeholder = 'Write here your question:') 
  if st.button('Answer me!'): 
    try:
      with st.spinner('In progress...'):
        client = OpenAI(api_key = password)
        model = model # os.environ['OPENAI_MODEL']
        response = client.chat.completions.create(model = model, messages = [{"role": "user", "content": question},])
        answer = response.choices[0].message.content.strip()
        message = st.chat_message('ai') # st.text(answer)
        message.write(answer)
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = 'Chat' + now + '.txt'
        answers.loc[len(answers)] = [model, question, answer]
        st.download_button(label = 'Download Chat', data = answers.to_csv(index = False).encode('utf-8'), file_name = filename) # ';'.join([model, mquestion, answer])
    except Exception as e:
      st.error(f'An Error happened: {e}')
  
  
elif selected == 'Image':
  
  password2 = st.text_input('Set your OpenAI API key:', type = 'password', value = os.environ['OPENAI_API_KEY'], placeholder = "If you don't have one, then you can create here: https://platform.openai.com/api-keys")
  model2 = st.selectbox('Choose AI Model:', options = ['dall-e-3', 'gpt-image-1', 'gpt-image-0721-mini-alpha', 'dall-e-2'])
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
        # urllib.request.urlretrieve(response.data[0].url, filename)
        
        link = response.data[0].url
        gallery.append(link)
        r = requests.get(link)
        
        left_co, cent_co,last_co = st.columns(3)
        with cent_co:
          st.image(link)
          st.download_button(label = 'Download Image',
                            data = BytesIO(r.content),
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
      r = requests.get(gallery[0])
      st.download_button(label = 'Download Image',
                          data = BytesIO(r.content),
                          file_name = filename,
                          mime = 'image/png')
                          
    elif len(gallery) > 1:
      PictureRow = st.slider('Choose picture from your actual online gallery:', 0, len(gallery) - 1, 0)
      st.image(gallery[PictureRow])
      
      now = datetime.now().strftime('%Y%m%d%H%M%S')
      filename = 'image' + now + '.png'
      r = requests.get(gallery[PictureRow])
      st.download_button(label = 'Download Image',
                          data = BytesIO(r.content),
                          file_name = filename,
                          mime = 'image/png')
  
    else:
      st.success("You didn't make any image in this online session still.")
