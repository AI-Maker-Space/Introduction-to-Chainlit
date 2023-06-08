FROM 3.8.17-alpine3.18
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["chainlit", "app.py", "--port", "7860"]