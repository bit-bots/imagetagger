#! /bin/bash
if [[ -z $1 ]]; then
    echo "No imageset specified!"
    exit 1
fi
echo "Please enter Username and Password for the imagetagger. This script will download into the current directory"
read -p "User: " USER
read -s -p "Password: " PASSWD

BASEURL="{{ base_url }}"
TMP=`mktemp -d imagetagger-XXXX`
IFS=','

echo ""
# Login
CSRF=`wget -nv --keep-session-cookies --save-cookies ${TMP}/cookie ${BASEURL} -O - | grep csrfmiddlewaretoken | tail -n 1 | sed -E "s/.*value='(.*)' .*/\1/g"`
wget -nv --referer ${BASEURL}{% url 'users:login' %} --keep-session-cookies --save-cookies ${TMP}/cookie --load-cookies ${TMP}/cookie --post-data "username=${USER}&password=${PASSWD}&csrfmiddlewaretoken=$CSRF&login" $BASEURL{% url 'users:login' %} -O - >/dev/null
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
    image=`echo ${image} | tail -1`
    imagename=${image##*'?'}
    imagepath=${image%%'?'*}
    if ! wget -nv --keep-session-cookies --save-cookies ${TMP}/cookie --load-cookies ${TMP}/cookie --trust-server-names --content-disposition -O ${imagename} ${BASEURL}${imagepath}; then
        echo "Download Failed" 
        exit 2
    fi
done
