FROM python
ENV DISPLAY=:99
COPY . /Benchmark
RUN apt-get update && \
    apt-get install -y curl unzip xvfb libxi6 libgconf-2-4 firefox-esr && \
    mkdir -p tmp && \
    curl -L -o /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz && \
    tar -xvf /tmp/geckodriver.tar.gz -C /tmp && \
    mv /tmp/geckodriver /usr/local/bin/geckodriver && \
    chmod +x /usr/local/bin/geckodriver && \
    pip install -r /Benchmark/requirements.txt
CMD /bin/bash -c 'Xvfb :99 -ac & ; python /Benchmark/benchmark.py ;'