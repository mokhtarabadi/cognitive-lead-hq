# Optional Psiphon HTTP/SOCKS egress for blowsh.
#
# The binary is fetched from the official Psiphon binaries repository at build
# time, so the image ships with Psiphon inside. The config is baked with a US
# egress preference and loopback binding of the local proxy ports. Publish no
# host ports and keep the container on a bridge network shared with blowsh.
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq \
    && apt-get install -y -qq --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL -o /usr/local/bin/psiphon-tunnel-core \
       https://github.com/Psiphon-Labs/psiphon-tunnel-core-binaries/raw/master/linux/psiphon-tunnel-core-x86_64 \
    && chmod 0755 /usr/local/bin/psiphon-tunnel-core

COPY psiphon.config /etc/psiphon/psiphon.config

EXPOSE 8082 1081

HEALTHCHECK --interval=60s --timeout=30s --retries=5 --start-period=120s \
    CMD curl -x http://127.0.0.1:8082 -fsSL --max-time 25 \
        https://www.cloudflare.com/cdn-cgi/trace | grep -q '^loc=' || exit 1

ENTRYPOINT ["/usr/local/bin/psiphon-tunnel-core", "-config", "/etc/psiphon/psiphon.config"]
