FROM 3.8.17-alpine3.18
# copy the requirements.txt file first to avoid cache invalidations
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app
CMD ["chainlit", "app.py", "--port", "7860"]