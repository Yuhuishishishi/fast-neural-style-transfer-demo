FROM continuumio/miniconda

RUN /bin/bash -c "conda create -n web python=3.6 && \
    source activate web && \
    conda install pytorch-cpu torchvision-cpu -c pytorch -y && \
    conda install flask gunicorn flask-wtf -y"

ADD . /opt/fnst

EXPOSE 5000

WORKDIR /opt/fnst/app

RUN chmod +x boot.sh

CMD ["./boot.sh"]



