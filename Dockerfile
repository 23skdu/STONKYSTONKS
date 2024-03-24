FROM python:3.11
LABEL author=23skdu@users.noreply.github.com
RUN set +x && apt update && apt -y upgrade && apt -y install netcat-traditional \
    && pip3 install googlefinance gspread oauth2client newrelic prometheus-client yfinance numpy pandas matplotlib tensorflow[and-cuda] keras scikit-learn plotly argparse requests \
    && pip3 cache purge && rm -rf /var/cache/apt
COPY stonky /bin
CMD ["nc","-l", "8888"] 
