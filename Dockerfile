FROM python:3.9
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["chainlit", "app.py", "--port", "7860"]