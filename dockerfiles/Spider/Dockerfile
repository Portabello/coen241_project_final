FROM python
COPY spiders/* /spiders
RUN apt clean \
    && apt-get update 
CMD /bin/bash
