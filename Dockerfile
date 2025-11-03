FROM nginx:1.25-alpine

# Clean default html
RUN rm -rf /usr/share/nginx/html/*

# Copy our nginx config and static site
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY web/ /usr/share/nginx/html/

# Expose port
EXPOSE 80

# Default command provided by base image starts nginx

