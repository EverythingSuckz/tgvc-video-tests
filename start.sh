#!/bin/bash

install_required_stuffs () {
    pip3 install –upgrade pip
    apt -qq update -y
    apt -qq install -y --no-install-recommends \
        git \
        ffmpeg \
        mediainfo \
        unzip \
        wget \
        gifsicle 
}

print_banner () {
    echo "
+=============================================+
       *      *  ___ __  .   __          . 
           .      | /__ \ / /      *       
    .             | \_|  V  \__         .  
*        *    *        __     *    .    
     \ /o  _| _  _    (_ _|_ __ _  _ __.
   .  V | (_|(/_(_)   __) |_ | (/_(_||||
+=============================================+
    "
}

install_py_requirements () {
    pip3 install -U setuptools wheel
    pip3 install --no-cache-dir -r requirements.
}

print_banner
install_required_stuffs
install_py_requirements
python3 -m vcbot