#!/bin/bash
# usage: check/replace/serivce_wait/service_start
cd $(dirname $0)
echo

# version
if [ -f ${APP_HOME}/${APP_NAME}/VERSION ]; then
    echo -e "Checking env for ${APP_NAME}..\n`cat ${APP_HOME}/${APP_NAME}/VERSION`"
else
    echo "Checking env for ${APP_NAME}.."
fi

# check dir
if [ -d ../conf ]; then
    cd ../conf
else
    echo "please put conf/ and start.sh to the same directory."
    exit 1
fi

# get conf files
CONF_FILES=`find $(pwd) -type f | grep -v "\.svn" | grep -v "\.git"`

# if no config file exists
if [ -z "$CONF_FILES" ]; then
    echo "No conf files found, pass."
fi

# has config file
for f in $CONF_FILES; do

    # metadata => "<location:LOCATION_OF_FILE> [MODE:600] [OWNER:USERNAME]"
    # if there is " " " in value, use "\"  to escape
    # use "${APP_HOME}/${APP_NAME}" to module home

    # dos2unix
    if which dos2unix &>/dev/null; then
        dos2unix $f
    else
        sed -i 's/.$//' $f
    fi

    # get the location of metadata
    METADATA_LOCATION=$(grep -iw metadata $f | awk -F'=>' '{print $2}' | \
                      awk -F'location:' '{print $2}' | sed -n '1p' | \
                      awk '{print $1}' | tr -d ',;"' | tr -d "'")

    # replace the variable to true path
    METADATA_LOCATION=`eval echo $METADATA_LOCATION`

    # there is no location tag of metadata
    if [ -z "$METADATA_LOCATION" ]; then
        echo "\"location\" of metadata in \"$f\" not define!"
        check_passed="$check_passed false"
        continue
    else
        # if is a path
        if `dirname $METADATA_LOCATION &>/dev/null`; then

            # if does not exist, mkdir
            if ! [ -d "$(dirname $METADATA_LOCATION)" ]; then
                echo "mkdir -p $(dirname $METADATA_LOCATION)"
                mkdir -p $(dirname $METADATA_LOCATION)
            fi
        else
            echo "\"location\" of metadata in \"$f\" not PATH format!"
            check_passed="$check_passed false"
            continue
        fi
        dockerize_template="${dockerize_template} -template ${f}:${METADATA_LOCATION}"
    fi

    # has location but no {{ VAR }}
    VAR_IN_BRACE=$(grep {{.*}} $f | sed -n 's/.*{{ *\(.*\) *}}.*/\1/p')
    if [ -z "$VAR_IN_BRACE" ]; then
        echo "skip \"${f}\" without replacing, pass."
        continue

    # has location and {{ VAR }}
    else
        # loop to check
        for i in $VAR_IN_BRACE; do
            VAR_TO_CHECK=${i##.Env.}
            VAR_TO_CHECK=`echo $VAR_TO_CHECK`

            # Check the value
            if [ -z "${!VAR_TO_CHECK}" ]; then
                echo "Can not get env: \"${VAR_TO_CHECK}\" in file: \"$f\" !"
                check_passed="$check_passed false"
            else
                echo "|- ${VAR_TO_CHECK}=${!VAR_TO_CHECK}"
            fi
        done
    fi
done

# if error, exit
if echo $check_passed | grep -wq "false"; then
    echo
    echo "To inject variables to container, you can do it in:"
    echo "  1. Dockerfile"
    echo "  2. compose file (recommand)"
    echo "  3. docker run with \"-e\" option"
    echo "And you can receive value with \"{{ .Env.VARIABLE_NAME }}\" in config file."
    echo
    exit 1
else
    echo "Env check pass."
    echo
fi

# get dependice
for i in ${!APP_DEP*}; do
    dockerize_wait="${dockerize_wait} -wait ${!i}"
done


# replace、Serivce wait、Service start
echo -n "Pre-starting.."
dockerize \
    ${dockerize_template} \
    ${dockerize_wait} -timeout 1200s \
    -stdout    /var/log/${APP_NAME}.log \
    -stderr    /var/log/${APP_NAME}.log \
    echo "done"
echo


# start, important
Service_Start() {
    echo "Starting ${APP_NAME}.."

    ####### START COMMAND HERE #########
    set -e
    start_${APP_NAME} && \
    echo "success" && \
    tail -f /var/log/${APP_NAME}.log

    ####################################

}

# default: start the service
Service_Start



