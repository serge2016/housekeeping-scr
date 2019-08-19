FROM ubuntu:14.04
LABEL maintainer="serge2016"

# Author: Serge I. Mitrofanov.
# LastUpdate: 29.07.2018 18:00.

# Tool type: infrastructure

# Contents:
#   memUsage.

# Input:

# Output:


ENV DEBIAN_FRONTEND="noninteractive"

RUN apt-get update && apt-get --yes --force-yes --no-install-recommends install \
    build-essential \
    pkg-config \
    software-properties-common \
    ncurses-dev \
    curl \
    wget \
    nano \
    time \
    tcsh \
    gawk \
    bzip2 \
    pigz \
    zip \
    unzip \
    xz-utils \
    mc \
    htop \
    iotop \
    git-core \
    subversion \
    python \
    python-tk \
    python-dev \
    python-setuptools \
    openssh-client \
    openssl \
    libssl-dev \
    libyaml-dev \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libpq-dev \
    realpath

ENV TZ="Europe/Moscow"
RUN echo $TZ > /etc/timezone \
    && dpkg-reconfigure tzdata

ENV TMPDIR="/tmp"
RUN mkdir -p "$TMPDIR"

ENV SOFT="/soft"
RUN mkdir -p "$SOFT"

# memUsage (both python 2 & 3) (Olga)
# psutil >= 2.2.1 (Tested with 5.6.1 - ok; 1.2.1 - err) - additional python package required for memUsage. That's why apt install python-psutil doesn't fit on Ubuntu 14.04
RUN cd "$SOFT" \
    && wget -q "https://github.com/giampaolo/psutil/archive/release-5.6.3.tar.gz" -O "$SOFT/psutil-release-5.6.3.tar.gz" \
    && tar -xzf "$SOFT/psutil-release-5.6.3.tar.gz" \
    && cd "$SOFT/psutil-release-5.6.3" \
    && python setup.py install \
    && cd "$SOFT" \
    && rm -r "$SOFT/psutil-release-5.6.3" \
    && mkdir -p "$SOFT/memusage/bin" \
    && wget -q "https://raw.githubusercontent.com/serge2016/memUsage/master/memUsage.py" -O - | tr -d '\r' > "$SOFT/memusage/bin/memUsage.py" \
    && chmod +x "$SOFT/memusage/bin/memUsage.py"
ENV MEMUSAGE="$SOFT/memusage/bin/memUsage.py" \
    PATH="$SOFT/memusage/bin:$PATH"

RUN apt-get clean \
    && rm -rf /var/lib/apt/lists

WORKDIR /outputs
