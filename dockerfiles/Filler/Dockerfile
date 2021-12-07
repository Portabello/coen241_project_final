FROM python
COPY spiders/* /spiders/
RUN cd spiders \
    && curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add \
    && bash -c "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list" \
    && apt -y update \
    && apt -y install google-chrome-stable \
    && wget https://chromedriver.storage.googleapis.com/96.0.4664.45/chromedriver_linux64.zip\
    && unzip chromedriver_linux64.zip \
    && python -m pip install --upgrade pip \
    && pip install -r /spiders/requirements.txt
CMD cd spiders; scrapy runspider cnn_spider_filler.py
