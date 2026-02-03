import streamlit as st
import os
from openai import OpenAI
from streamlit_option_menu import option_menu
from datetime import datetime
import pandas as pd
from io import BytesIO
import requests
import base64
from sqlalchemy import text
# from PIL import Image

@st.cache_resource
def initialization_function():
  answers = pd.DataFrame(columns = ['Model', 'Question', 'Answer'])
  return answers

@st.cache_resource
def initialization_function2():
  gallery = []
  return gallery

@st.cache_resource
def initialization_function3():
  video_gallery = []
  return video_gallery
    
answers = initialization_function()
gallery = initialization_function2()
video_gallery = initialization_function3()

st.set_page_config(
  layout = 'wide',
  page_title = 'Ask AI with Python',
  page_icon = 'ikon.png', # https://map.ksh.hu/timea/images/shortcut.ico
  menu_items = {'Get help': 'mailto:adam.szilagyi@ksh.hu',
                'Report a bug': 'mailto:adam.szilagyi@ksh.hu',
                'About': 'This webapplication makes you able to chat and generate picture with ChatGPT through OpenAI module.'}
  )


if not st.user.is_logged_in:
  if st.button("Login with Google"):
    st.login() # Elindítja az OAuth folyamatot
else:
  st.write(f"Greetings, {st.user.name}!")
  # st.write(f"E-mail: {st.user.email}")
    
  if st.button("Logout"):
    st.logout()

conn = st.connection("postgresql", type = "sql")

try:
  with conn.session as session:
    session.execute(text("""CREATE TABLE IF NOT EXISTS chats (
      id SERIAL PRIMARY KEY, 
      email TEXT UNIQUE, 
      model VARCHAR(30), 
      question TEXT UNIQUE, 
      answer TEXT UNIQUE, 
      date timestamp)"""))
    # st.dataframe(session.query())
    session.commit()
    # st.success("Table 'chats' created successfully!")
except Exception as e:
  st.error(f"Error creating table: {e}")
    
st.title('Ask AI with Python')
password = st.text_input('Set your OpenAI API key:', type = 'password', value = os.environ['OPENAI_API_KEY'], placeholder = "If you don't have one, then you can create here: https://platform.openai.com/api-keys", key = "my_key") # st.session_state.my_text 
selected = option_menu(None, ['Chat', 'Messages', 'Image', 'Picture Gallery', 'Video', 'Video Gallery'], menu_icon = 'cast', default_index = 0, orientation = 'horizontal')

if selected == 'Chat': 
  
  model = st.selectbox('Choose AI Model:', options = ['gpt-5.2', 'gpt-5', 'gpt-5-mini', 'gpt-5-nano'])
  question = st.text_area('Write here your question:', placeholder = 'Ask something!', value = None) # question = st.chat_input(placeholder = 'Write here your question:') 
  
  if st.button('Answer me!'): 
    try:
      with st.spinner('In progress...'):
        client = OpenAI(api_key = password)
        model = model # os.environ['OPENAI_MODEL']
        response = client.chat.completions.create(model = model, messages = [{"role": "system", "content": "You are a helpful assistant. Answer as short as possible."}, {"role": "user", "content": question}], temperature = 0)
        answer = response.choices[0].message.content.strip()
        st.text(answer) # message = st.chat_message('ai')
        # message.write(answer)
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = 'Chat' + now + '.txt'
        answers.loc[len(answers)] = [model, question, answer]
        
        if st.user.is_logged_in:
          try:
            with conn.session as session:
              session.execute(text("""INSERT INTO chats(email, model, question, answer, date) VALUES (:email, :model, :question, :answer, :date)"""), {"email": st.user.email, "model": model, "question": question, "answer": answer, "date": datetime.now()})
              session.commit()
              # st.success("Adatok sikeresen elmentve!")
          except Exception as e:
            st.error(f"Hiba történt: {e}")
        
        st.download_button(label = 'Download Chat', data = answers.to_csv(index = False, sep = ';').encode('utf-8'), file_name = filename) # ';'.join([model, mquestion, answer])
    except Exception as e:
      st.error(f'An Error happened: {e}')

elif selected == 'Messages':
  element = st.dataframe(answers, hide_index = True) # st.session_state.df

elif selected == 'Image':
  
  model2 = st.selectbox('Choose AI Model:', options = ['dall-e-3', 'chatgpt-image-latest', 'gpt-image-1.5', 'gpt-image-1', 'gpt-image-1-mini']) #  'gpt-image-1', 'gpt-image-1-mini', 'gpt-image-1.5', 'chatgpt-image-latest', 'dall-e-2', and 'dall-e-3'.
  desciption = st.text_area('What should the picture depict?', placeholder = 'Describe here...')
  if st.button('Draw me!'):
    try:
      with st.spinner('In progress...'):
        client = OpenAI(api_key = password)
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
          # st.success(f"You can find your image at the Galery or on the next link: {link}")
        else:
          image_base64 = response.data[0].b64_json
          image_bytes = base64.b64decode(image_base64)
          gallery.append(image_bytes)
          # st.success(f"You can find your image at the Galery.")
          
        # image_bytes.seek(0)
        # image = Image.open(image_bytes)
          
        left_co, cent_co,last_co = st.columns(3)
        with cent_co:
          st.image(gallery[-1])
          # st.image(image_bytes)
            
          # st.download_button(label = 'Download Image',
          #                    data = gallery[-1], # image_bytes, # BytesIO(r.content)
          #                    file_name = filename,
          #                    mime = 'image/png')
          
    except Exception as e:
      st.error(f'An Error happened: {e}')
  
elif selected == 'Picture Gallery':
  
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

elif selected == "Video":
  
  model3 = st.selectbox('Choose AI Model:', options = ['sora-2', 'sora-2-pro', 'sora-1'])
  duration = st.selectbox('Choose duration:', options = ['4', '8', '12'])
  # size = st.selectbox('Choose size:', options = ['1280x720', '720x1280'])
  content = st.text_area('Write here your question:', placeholder = 'What about the video?', value = None)
  
  try:
    if st.button('Shoot me!'):
      with st.spinner('In progress...'):
        client = OpenAI(api_key = password)
    
        video = client.videos.create(
          model = model3,
          prompt = content, # A futuristic city in the style of cyberpunk with neon lights. # A calico cat playing a piano on stage
          size = "1280x720", # Optional: 720x1280, 1280x720, 1024x1792, 1792x1024
          seconds = duration      # Optional: 4, 8, or 12 seconds
        )
      
        # print(video.id)
      
        completed_video = client.videos.retrieve(video.id) 
        # print(completed_video)
        while completed_video.status != "completed":
          completed_video = client.videos.retrieve(video.id)
          if completed_video.status == "failed":
            st.error(f"This video can not be created: {completed_video}") # : {completed_video.message}
            break
        
        if completed_video.status == "completed":
          # st.success(completed_video)
          st.success(f"You can download this video: {video.id}.mp4")
          video_content = client.videos.download_content(completed_video.id)
          video_bytes = video_content.read()
          video_gallery.append(video_bytes)
          st.video(video_bytes)
  except Exception as e:
    st.error(f'An Error happened: {e}')

elif selected == 'Video Gallery':
  
  left_co, cent_co,last_co = st.columns(3)
  with cent_co:
  
    if len(video_gallery) == 1:
      st.video(video_gallery[0])
      
      now = datetime.now().strftime('%Y%m%d%H%M%S')
      filename = 'video' + now + '.mp4'
      st.download_button(label = 'Download Video',
                          data = video_gallery[0], # BytesIO(r.content),
                          file_name = filename,
                          mime = 'image/png')
                          
    elif len(video_gallery) > 1:
      VideoRow = st.slider('Choose video from your actual online gallery:', 0, len(video_gallery) - 1, 0)
      st.video(video_gallery[VideoRow])
      
      now = datetime.now().strftime('%Y%m%d%H%M%S')
      filename = 'video' + now + '.mp4'
      st.download_button(label = 'Download Video',
                          data = video_gallery[VideoRow], # BytesIO(r.content),
                          file_name = filename,
                          mime = 'video/mp4')
  
    else:
      st.success("You didn't make any video in this online session still.")
