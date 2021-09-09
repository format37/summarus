FROM python:latest
WORKDIR /worker
COPY requirements.txt /worker
RUN pip3 install -r requirements.txt --no-cache-dir
COPY summarus_cpu_worker.py /worker
ENTRYPOINT ["python3"]
CMD ["summarus_cpu_worker.py"]
