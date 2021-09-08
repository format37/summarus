FROM pytorch/pytorch
WORKDIR /summarus
COPY requirements.txt /summarus
RUN apt-get update -y; apt-get install -y gcc; apt-get install -y git
RUN python -m pip install -r requirements.txt
RUN conda install pytorch torchvision cudatoolkit=10.1 -c pytorch -y
COPY server.py /summarus
ENTRYPOINT ["python3"]
CMD ["server.py"]
