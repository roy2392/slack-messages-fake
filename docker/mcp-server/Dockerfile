FROM golang:1.24-alpine AS builder

WORKDIR /build

# Install git and make
RUN apk add --no-cache git make

# Clone and build Slack MCP server
RUN git clone https://github.com/korotovsky/slack-mcp-server.git && \
    cd slack-mcp-server && \
    make build

FROM alpine:latest

WORKDIR /app

# Copy binary from builder
COPY --from=builder /build/slack-mcp-server/build/slack-mcp-server /app/slack-mcp-server

# Install ca-certificates and wget for HTTPS and healthcheck
RUN apk add --no-cache ca-certificates wget

# Expose MCP server port
EXPOSE 13080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:13080/mcp || exit 1

# Run MCP server in HTTP mode
CMD ["/app/slack-mcp-server", "--transport", "http"]
