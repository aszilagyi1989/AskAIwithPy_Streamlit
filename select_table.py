import streamlit as st

conn = st.connection("postgresql", type = "sql")

df = conn.query('SELECT * FROM chats;', ttl = "10m")

st.title("Adatok a Render Postgres-ből")
st.dataframe(df)



# import streamlit as st
# 
# # Kapcsolat létrehozása
# conn = st.connection("postgresql", type="sql")
# 
# st.title("Adatfelvétel Render Postgres-be")
# 
# with st.form("my_form"):
#     name = st.text_input("Név")
#     age = st.number_input("Kor", min_value=0)
#     submitted = st.form_submit_button("Mentés")
# 
#     if submitted:
#         try:
#             with conn.session as session:
#                 # SQL beszúrás végrehajtása
#                 session.execute(
#                     "INSERT INTO users (name, age) VALUES (:name, :age);",
#                     {"name": name, "age": age}
#                 )
#                 session.commit() # Nagyon fontos a mentéshez!
#             st.success("Adatok sikeresen elmentve!")
#         except Exception as e:
#             st.error(f"Hiba történt: {e}")
