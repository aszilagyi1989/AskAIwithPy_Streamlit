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
import boto3
from botocore.exceptions import NoCredentialsError

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

@st.cache_resource
def databaseConnection():
  conn = st.connection("postgresql", type = "sql")
  return conn

@st.cache_resource
def amazon():
  s3 = boto3.client(
    's3',
    aws_access_key_id = st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key = st.secrets["AWS_SECRET_ACCESS_KEY"]
  )
  return s3

    
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
  st.info("If you have got an OpenAI API Key, then after sign in with Google you can use this web application with different AI models to chat and create photos and videos.")
  st.info("You can buy credits here: https://platform.openai.com/settings/organization/billing/overview")
  st.info("Your email address and other data like your questions and descriptions are saved into PostgreSQL database tables.")
  st.info("Your AI generated photos and videos are stored on Amazon locally.")
  if st.button("Login with Google"):
    st.login() # Elindítja az OAuth folyamatot
  st.stop()
else:
  st.write(f"Greetings, {st.user.name}!")
    
  if st.button("Logout"):
    st.logout()

conn = databaseConnection()
s3 = amazon()

try:
  with conn.session as session:
    # session.execute(text("DROP TABLE IF EXISTS chats"))
    # session.commit()
    # 
    # session.execute(text("DROP TABLE IF EXISTS images"))
    # session.commit()
    # 
    # session.execute(text("DROP TABLE IF EXISTS videos"))
    # session.commit()
        
    session.execute(text("""CREATE TABLE IF NOT EXISTS chats (
      id SERIAL PRIMARY KEY, 
      email TEXT, 
      model VARCHAR(30), 
      question TEXT, 
      answer TEXT, 
      date timestamp DEFAULT CURRENT_TIMESTAMP)"""))
    session.commit()
    
    session.execute(text("""CREATE TABLE IF NOT EXISTS images (
      id SERIAL PRIMARY KEY, 
      email TEXT, 
      model VARCHAR(30), 
      description TEXT, 
      image TEXT, 
      date timestamp DEFAULT CURRENT_TIMESTAMP)"""))
    session.commit()
    
    session.execute(text("""CREATE TABLE IF NOT EXISTS videos (
      id SERIAL PRIMARY KEY, 
      email TEXT, 
      model VARCHAR(30), 
      content TEXT, 
      video TEXT, 
      date timestamp DEFAULT CURRENT_TIMESTAMP)"""))
    session.commit()
    
    
except Exception as e:
  st.error(f"Error creating table: {e}")
    
st.title('Ask AI with Python', anchor = False, help = None)
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
              session.execute(text("""INSERT INTO chats(email, model, question, answer) VALUES (:email, :model, :question, :answer)"""), {"email": st.user.email, "model": model, "question": question, "answer": answer})
              session.commit()
          except Exception as e:
            st.error(f"Hiba történt: {e}")
        
        st.download_button(label = 'Download Chat', data = answers.to_csv(index = False, sep = ';').encode('utf-8'), file_name = filename) # ';'.join([model, mquestion, answer])
    except Exception as e:
      st.error(f'An Error happened: {e}')

elif selected == 'Messages':
  if st.user.is_logged_in:
    df = conn.query("SELECT model, question, answer FROM chats", ttl = 0) # None "10m"
    # df = conn.query("SELECT * FROM chats WHERE model = :name", params={"name": "gpt-4"})
    element = st.dataframe(df, hide_index = True)
  else:
    element = st.dataframe(answers, hide_index = True) # st.session_state.df

elif selected == 'Image':
  
  model2 = st.selectbox('Choose AI Model:', options = ['dall-e-3', 'chatgpt-image-latest', 'gpt-image-1.5', 'gpt-image-1', 'gpt-image-1-mini']) #  'gpt-image-1', 'gpt-image-1-mini', 'gpt-image-1.5', 'chatgpt-image-latest', 'dall-e-2', and 'dall-e-3'.
  description = st.text_area('What should the picture depict?', placeholder = 'Describe here...')
  if st.button('Draw me!'):
    try:
      with st.spinner('In progress...'):
        client = OpenAI(api_key = password)
        response = client.images.generate(
          model = model2, 
          prompt = description, 
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
          image_bytes = BytesIO(image_bytes)
          
        if st.user.is_logged_in:
          try:
            s3.put_object(
              Bucket = 'askaiwithpy', 
              Key = filename, 
              Body = image_bytes.getvalue()
          )
          except NoCredentialsError:
            st.error(f"Hiba történt a kép feltöltése során: {e}")
            
          try:
            with conn.session as session:
              session.execute(text("""INSERT INTO images(email, model, description, image) VALUES (:email, :model, :description, :image)"""), {"email": st.user.email, "model": model2, "description": description, "image": f"https://askaiwithpy.s3.eu-north-1.amazonaws.com/{filename}"})
              session.commit()
              st.success("Beszúrtam")
          except Exception as e:
            st.error(f"Hiba történt: {e}")
          
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
  
  if st.user.is_logged_in:
    df = conn.query("SELECT * FROM images", ttl = 0)
    
    with cent_co:
    
      if len(df) == 1:
        
        st.image(df['image'].iloc[0])
        
        response = requests.get(df['image'].iloc[0])
        image_bytes = response.content
        
        st.download_button(label = 'Download Image',
                            data = image_bytes,
                            file_name = df['image'].iloc[0][-23:],
                            mime = 'image/png')
                            
      elif len(df) > 1:
        
        PictureRow = st.slider('Choose picture from your gallery:', 0, len(df) - 1, 0)
        st.image(df['image'].iloc[PictureRow])
        
        response = requests.get(df['image'].iloc[PictureRow])
        image_bytes = response.content

        st.download_button(label = 'Download Image',
                            data = image_bytes,
                            file_name = df['image'].iloc[PictureRow][-23:],
                            mime = 'image/png')
    
      else:
        st.success("You didn't make any image still.")

  else:
    
    with cent_co:
    
      if len(gallery) == 1:
        st.image(gallery[0])
        
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = 'image' + now + '.png'
        st.download_button(label = 'Download Image',
                            data = gallery[0], 
                            file_name = filename,
                            mime = 'image/png')
                            
      elif len(gallery) > 1:
        
        PictureRow = st.slider('Choose picture from your actual online gallery:', 0, len(gallery) - 1, 0)
        st.image(gallery[PictureRow])
        
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = 'image' + now + '.png'
        st.download_button(label = 'Download Image',
                            data = gallery[PictureRow],
                            file_name = filename,
                            mime = 'image/png')
    
      else:
        st.success("You didn't make any image in this online session still.")

elif selected == "Video":
  
  model3 = st.selectbox('Choose AI Model:', options = ['sora-2', 'sora-2-pro', 'sora-2-2025-10-06', 'sora-2-2025-12-08'])
  duration = st.selectbox('Choose duration:', options = ['4', '8', '12'])
  # size = st.selectbox('Choose size:', options = ['1280x720', '720x1280'])
  content = st.text_area('Write here the story of the video:', placeholder = 'Story of the video?', value = None)
  
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
          
          if st.user.is_logged_in:
            try:
              s3.put_object(
                Bucket = 'askaiwithpy', 
                Key = f"{video.id}", 
                Body = video_bytes # .getvalue()
            )
            except NoCredentialsError:
              st.error(f"Hiba történt a videó feltöltése során: {e}")
              
            try:
              with conn.session as session:
                session.execute(text("""INSERT INTO videos(email, model, content, video) VALUES (:email, :model, :content, :video)"""), {"email": st.user.email, "model": model3, "content": content, "video": f"https://askaiwithpy.s3.eu-north-1.amazonaws.com/{video.id}"})
                session.commit()
            except Exception as e:
              st.error(f"Hiba történt a videó linkjének mentése közben: {e}")
              
  except Exception as e:
    st.error(f'An Error happened: {e}')

elif selected == 'Video Gallery':
  
  left_co, cent_co,last_co = st.columns(3)
  
  if st.user.is_logged_in:
    df = conn.query("SELECT * FROM videos", ttl = 0)
    
    with cent_co:
    
      if len(df) == 1:
        
        st.video(df['video'].iloc[0])
        
        response = requests.get(df['video'].iloc[0])
        image_bytes = response.content
        st.download_button(label = 'Download Video',
                            data = image_bytes,
                            file_name = f"video_{str(df['video'].iloc[0]).split("_")[1]}.mp4",
                            mime = 'video/mp4')
                            
      elif len(df) > 1:
        
        PictureRow = st.slider('Choose video from your gallery:', 0, len(df) - 1, 0)
        st.video(df['video'].iloc[PictureRow])
        
        response = requests.get(df['video'].iloc[PictureRow])
        image_bytes = response.content

        st.download_button(label = 'Download Video',
                            data = image_bytes,
                            file_name = f"video_{str(df['video'].iloc[PictureRow]).split("_")[1]}.mp4",
                            mime = 'video/mp4')
    
      else:
        st.success("You didn't make any video still.")

  else:
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
