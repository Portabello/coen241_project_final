FROM python
COPY spiders/* /spiders/
RUN python -m pip install --upgrade pip \
    && pip install -r /spiders/requirements.txt
CMD /bin/bash
