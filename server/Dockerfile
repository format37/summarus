FROM pytorch/pytorch
COPY requirements.txt .
RUN apt-get update -y; apt-get install -y gcc; apt-get install -y git
RUN python -m pip install -r requirements.txt
RUN conda install pytorch torchvision cudatoolkit=10.1 -c pytorch -y
ADD scripts/* /server/
WORKDIR /server/
RUN python docker_init.py
# ENTRYPOINT ["python", "server.py"]
