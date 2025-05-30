# fritzflare-dyndns

**fritzflare-dyndns** is a lightweight, containerized utility for updating Cloudflare DNS A-records, designed for dynamic IP environments such as home networks using Fritz!Box routers. Run it easily as a Docker container for reliable dynamic DNS (DDNS) updates.

**Example:**

```
CLOUDFLARE_DNS_HOSTNAMES=example.com,www.example.com
```
This will update the A record for `@` in zone `example.com` and the A record for `www` in zone `example.com`.

---

## Features

- Updates Cloudflare DNS A-records automatically
- Designed for dynamic IP scenarios (e.g., home routers)
- Runs as a minimal Docker container

---

## Environment Variables

| Variable                | Required | Description                                                        |
|-------------------------|----------|--------------------------------------------------------------------|
| `CLOUDFLARE_API_TOKEN`  | Yes      | Cloudflare API token with DNS edit permissions                     |
| `CLOUDFLARE_DNS_HOSTNAMES` | Yes      | Comma-separated list of hostnames/subdomains to update A (IPv4) and AAAA (IPv6) records.  |

---

## How to Run with Docker

1. **Build the Docker Image**

   ```bash
   docker build -t fritzflare-dyndns .
   ```

2. **Run the Docker Container**

   Replace `your_cloudflare_api_token` with your actual token.

   ```bash
   docker run -e CLOUDFLARE_API_TOKEN=your_cloudflare_api_token fritzflare-dyndns
   ```

   If your application exposes a web interface or API (for example, on port 8080), you can bind the port:

   ```bash
   docker run -e CLOUDFLARE_API_TOKEN=your_cloudflare_api_token -p 8080:8080 fritzflare-dyndns
   ```

   > **Note:** If your app does not expose a port, you can omit the `-p` flag.

---

## Example Usage

```bash
docker run -e CLOUDFLARE_API_TOKEN=your_cloudflare_api_token fritzflare-dyndns
```