FROM python:3.11
LABEL author=23skdu@users.noreply.github.com
RUN set +x && apt update && apt -y upgrade && apt -y install netcat-traditional \
    && pip3 install yfinance numpy pandas matplotlib seaborn scipy scikit-learn tensorflow[and-cuda] pyyaml \
    && pip3 cache purge && rm -rf /var/cache/apt
COPY stonky *.py /bin/
RUN chmod +x /bin/stonky /bin/*.py
CMD ["nc","-l", "8888"] 
