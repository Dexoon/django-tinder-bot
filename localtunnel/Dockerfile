FROM node:current-alpine

RUN npm install -g localtunnel
RUN apk add uuidgen bash
COPY uuid.sh /uuid.sh

ENTRYPOINT ["/uuid.sh"]
#ENTRYPOINT ["lt","--subdomain","sh", "-c","echo $UUID"]