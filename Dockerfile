FROM python
ENV DISPLAY=:99
COPY . /Benchmark
RUN ["Benchmark/init"]
CMD python /Benchmark/benchmark.py