FROM python:3.8.5
EXPOSE 8501
VOLUME ["/ExplorationDataApp"]
WORKDIR /ExplorationDataApp
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD streamlit run Explorapp.py
