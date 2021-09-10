FROM python:latest
WORKDIR /marker
COPY requirements.txt /marker
RUN pip3 install -r requirements.txt --no-cache-dir
COPY marker.py /marker
ENTRYPOINT ["python3"]
CMD ["marker.py"]
