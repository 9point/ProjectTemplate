
TEMPLATE_FILE=job.yml.template
JOB_ID=${PROJECT_NAME}-$(echo $(uuidgen) | tr '[:upper:]' '[:lower:]')
TEMP_DIR=./tmp/
JOB_FILENAME=${TEMP_DIR}${JOB_ID}.yml
IMAGE_NAME_ESC=$(echo ${IMAGE_NAME} | sed "s=/=\\\\/=g")

mkdir -p ${TEMP_DIR}

echo "Generating job file..."

cat $TEMPLATE_FILE \
  | sed -e "s/{{ name }}/${JOB_ID}/g" \
  | sed -e "s/{{ workflow-name }}/${WORKFLOW_NAME}/g" \
  | sed -e "s={{ image-name }}=${IMAGE_NAME}=g" \
  > ${JOB_FILENAME}

echo "Creating job..."

kubectl apply -f ${JOB_FILENAME}
