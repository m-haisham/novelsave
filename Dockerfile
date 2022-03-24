FROM python:3.9
RUN mkdir /app
WORKDIR /app
ADD . /app/
RUN pip install -r requirements.txt
CMD ["python", "-m", "novelsave", "runbot", "discord"]
