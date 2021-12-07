FROM python
COPY scheduler.py /
RUN python -m pip install --upgrade pip \
    && pip install pymongo pika
CMD python scheduler.py
