FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy go mod files
COPY server/go.mod server/go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY server/ .

# Build the application
RUN CGO_ENABLED=1 GOOS=linux go build -o server .

# Final stage
FROM alpine:latest

# Install ca-certificates and sqlite
RUN apk --no-cache add ca-certificates sqlite

WORKDIR /app

# Copy binary from builder stage
COPY --from=builder /app/server .

# Expose port
EXPOSE 4321

# Start the server
CMD ["./server"]