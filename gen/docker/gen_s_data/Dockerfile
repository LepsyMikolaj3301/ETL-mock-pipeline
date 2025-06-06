FROM python:3.12-slim


WORKDIR /app
COPY /gen_s_data /app

# If you have requirements.txt, copy and install it

RUN pip install -r requirements.txt


CMD ["python", "structured_data_gen.py"]