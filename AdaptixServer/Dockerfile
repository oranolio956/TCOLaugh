FROM golang:1.24.4-bookworm AS builder

# Install build dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=1 GOOS=linux go build -a -installsuffix cgo -o main .

# Final stage
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the binary
COPY --from=builder /app/main .

# Create directories for data
RUN mkdir -p /app/data /app/extenders

# Expose port
EXPOSE 10000

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=10000
ENV ENDPOINT=/
ENV DEBUG=false

# Run the application
CMD ["./main"]