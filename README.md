# HttpServer

A lightweight static site packaged with nginx so you can host the assets under `web/` for demos, testing, or internal tooling.

## Repository Layout

- `web/index.html` landing page served at `/`.
- `web/gallery.html` gallery page that expects images in `web/images/`.
- `web/images/` static image assets; keep `.gitkeep` if the folder is empty.
- `tools/generate_images.py` helper script that produces random noise images for load testing.
- `Dockerfile` builds an nginx image with the static content.
- `nginx.conf` nginx virtual host configuration shipped into the image.
- `requirements.txt` Python dependencies for the image generator script.

## Quick Start (Docker)

1. Build the container image: `docker build -t http-server .`
2. Run it locally: `docker run --rm -p 8080:80 http-server`
3. Visit `http://localhost:8080` for `index.html` or `http://localhost:8080/gallery.html` for the gallery.
4. Stop the container with `Ctrl+C` or by calling `docker stop` on the container id.

This serves the files from `web/` at `http://localhost:8080`. Disable caching in the browser when you test updates, because the gallery relies on fresh images.

## Managing Site Content

- Place HTML files under `web/`. The nginx config sets `/usr/share/nginx/html` to this directory inside the container.
- Put images and other assets in `web/images/`. The `/images/` path is autoindexed so you can fetch files directly when debugging.
- Update the links inside `index.html` or `gallery.html` to point to any new assets you add.
- Keep file names lowercase with no spaces to prevent broken links on case-sensitive hosts.

## Optional: Generate Sample Images

The repository ships with a helper script that creates random test images.

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python tools/generate_images.py --out web/images --count 12 --sizes 1024x1024,2000x2000 --format jpg --quality 85
```

On macOS or Linux replace the activation line with `source .venv/bin/activate`. Generated files land in `web/images/` and are available immediately to the server.

## How the Server Works

- The Dockerfile starts from `nginx:1.25-alpine`, removes the default site, copies `nginx.conf` and the `web/` folder into the image, and exposes port 80.
- `nginx.conf` serves files out of `/usr/share/nginx/html`, falls back to `404` when a path is missing, and enables directory listings just for `/images/` so you can inspect generated assets.
- Because the image is fully static, deployments are repeatable and very fast: you rebuild whenever site files change, then redeploy the container.

## Deploying

- Publish the image to your registry: `docker tag http-server <registry>/http-server:latest` followed by `docker push`.
- Run on any container host (Docker, Kubernetes, Azure Container Apps, etc.) with port 80 exposed. Behind a load balancer terminate TLS there or add a reverse proxy with certificates.
- To serve existing infrastructure, mount a volume at `/usr/share/nginx/html` when you `docker run` if you need to swap content without rebuilding.

## Troubleshooting

- If updates do not appear, clear the browser cache or hard refresh because static files can be cached aggressively.
- Check container logs with `docker logs <container>`; nginx errors about missing files usually indicate typos in file names or paths.
- Ensure any CDN or reverse proxy forwards requests for `/images/` if you rely on the autoindex feature.
