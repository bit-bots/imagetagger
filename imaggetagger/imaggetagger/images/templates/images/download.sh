#! /bin/bash

echo "Please enter Username and Password for imagetagger.mafiasi.de. This script will download into the current directory"
read -p "User: " USER
read -s -p "Password: " PASSWD

BASEURL="https://imagetagger.bit-bots.de"
TMP=`mktemp -d imagetagger-XXXX`

echo ""
# Login
CSRF=`wget -nv --keep-session-cookies --save-cookies ${TMP}/cookie ${BASEURL} -O - | grep csrfmiddlewaretoken | tail -n 1 | sed -E "s/.*value='(.*)' .*/\1/g"`
wget -nv --referer ${BASEURL}/login/ --keep-session-cookies --save-cookies ${TMP}/cookie --load-cookies ${TMP}/cookie --post-data "username=$USER&password=$PASSWD&csrfmiddlewaretoken=$CSRF" $BASEURL/login/ -O - >/dev/null
if grep --quiet sessionid ${TMP}/cookie; then
    echo "Login success"
else
    echo "Login failure"
    exit 1
fi
# Download images
images=`wget -nv --keep-session-cookies --save-cookies ${TMP}/cookie --load-cookies ${TMP}/cookie ${BASEURL}/images/imagelist/$1/ -O -`
for image in ${images}
  do
    if ! wget -nv --keep-session-cookies --save-cookies ${TMP}/cookie --load-cookies ${TMP}/cookie --trust-server-names --content-disposition ${BASEURL}${image}; then
        echo "Download Failed" 
        exit 2
    fi
done
