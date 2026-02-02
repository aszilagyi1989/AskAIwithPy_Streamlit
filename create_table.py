import streamlit as st
from sqlalchemy import text
conn = st.connection("postgresql", type = "sql")

if st.button('Create Table'):
  try:
    with conn.session as session:
      # session.execute(text("SET client_encoding TO 'UTF8'"))
      session.execute(text("""CREATE TABLE IF NOT EXISTS chats (id SERIAL PRIMARY KEY, email TEXT UNIQUE, model VARCHAR(30), question TEXT UNIQUE, answer TEXT UNIQUE, date timestamp)"""))
      session.commit()
      st.success("Table 'chats' created successfully!")
  except Exception as e:
    st.error(f"Error creating table: {e}")
    
    
# BYTEA
