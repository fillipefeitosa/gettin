FROM continuumio/miniconda3

ADD pandanaEnv.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml

# Get the name of environment from yml file
RUN echo "source activate $(head -1 /tmp/environment.yml | cut -d' ' -f2)" > ~/.bashrc
ENV PATH /opt/conda/envs/$(head -1 /tmp/environment.yml | cut -d' ' -f2)/bin:$PATH
