FROM nginx:alpine

WORKDIR /usr/share/nginx/html

RUN rm -rf ./*

COPY . .

EXPOSE 80

# start
CMD ["nginx", "-g", "daemon off;"]