FROM nvidia/cuda:13.0.2-cudnn-devel-ubuntu24.04

WORKDIR /
COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt
COPY rp_handler.py /

# Start the container
CMD ["python3", "-u", "rp_handler.py"]