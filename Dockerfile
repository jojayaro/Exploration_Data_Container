FROM python:3.8.5

COPY . /explorapp

WORKDIR /explorapp

RUN pip install -r requirements.txt

EXPOSE 8501

CMD streamlit run Explorapp.py
