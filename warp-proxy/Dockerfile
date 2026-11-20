# Optional Cloudflare WARP HTTP/SOCKS egress for blowsh.
#
# This is a thin, reproducible wrapper around the pinned upstream WARP image.
# It bakes the verified port configuration so the operator does not have to
# remember the upstream image's undocumented NET_PORT variable. Publish no
# host ports and keep the container on a bridge shared with blowsh.
FROM ghcr.io/mon-ius/docker-warp-socks:v8

LABEL org.opencontainers.image.title="blowsh-warp-proxy"
LABEL org.opencontainers.image.description="Optional Cloudflare WARP egress sidecar for blowsh"

ENV NET_PORT=9091
EXPOSE 9091
