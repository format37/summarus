FROM pytorch/pytorch
# FROM python

COPY requirements.txt .
RUN apt-get update -y; apt-get install -y gcc; apt-get install -y git; apt-get -y install redis-server
RUN python -m pip install -r requirements.txt
RUN conda install pytorch torchvision cudatoolkit=10.1 -c pytorch -y
# RUN -p 6379:6379 /bin/bash -c "python server.py"
EXPOSE 6379
COPY src/ .
#ENTRYPOINT ["echo hello"]
#ENTRYPOINT ["/bin/sh", "-c", "/opt/ngcsc/start.sh","-l","kubstaging","-ssl", "false", "-srv", "api"]
RUN python docker_init.py
ENTRYPOINT ["python", "server.py"]

