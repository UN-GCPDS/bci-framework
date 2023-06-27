FROM archlinux:base-devel

LABEL image="dunderlab/bci_framework"
LABEL version="1.2"

LABEL maintainer="yencardonaal@unal.edu.co"
LABEL description=""
LABEL project=""
LABEL documentation=""
LABEL license="BSD 2-Clause"

ENV QT_PLUGIN_PATH=/usr/lib/qt/plugins
ENV LD_LIBRARY_PATH=/usr/lib/qt/lib:$LD_LIBRARY_PATH

RUN pacman -Syu --needed --noconfirm git

ARG user=makepkg
RUN useradd --system --create-home $user \
    && echo "$user ALL=(ALL:ALL) NOPASSWD:ALL" > /etc/sudoers.d/$user
USER $user
WORKDIR /home/$user

RUN git clone https://aur.archlinux.org/yay.git \
    && cd yay \
    && makepkg -sri --needed --noconfirm \
    && cd \
    && rm -rf .cache yay

RUN yay -S --noconfirm kafka

USER root
RUN pacman -S python python-pip python-setuptools breeze-icons libglvnd libxkbcommon \
    fontconfig nss libxcomposite libxrender libxrandr libxtst alsa-lib \
    libxkbfile qt6 xcb-util xcb-util-wm xcb-util-keysyms \
    swig box2d \
    --overwrite='/usr/lib/python3.11/site-packages/platformdirs/*' --noconfirm \
    && pip install bci_framework mne==0.24 tensorflow gymnasium[box2d] joblib --break-system-packages

WORKDIR /app

EXPOSE 9092
EXPOSE 2181
EXPOSE 9999

COPY start-services.sh /start-services.sh
RUN chmod +x /start-services.sh

ENV ZOOKEEPER_PID_DIR=/run/kafka/
ENV LOG_DIR=/var/log/kafka
ENV KAFKA_LOG4J_OPTS="-Dlog4j.configuration=file:/etc/kafka/log4j.properties"

ADD start-services.sh /start-services.sh
RUN chmod +x /start-services.sh

RUN useradd -ms /bin/bash user

CMD ["/start-services.sh"]
