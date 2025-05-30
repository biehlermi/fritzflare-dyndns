# fritzflare-dyndns

**fritzflare-dyndns** is a lightweight, containerized utility for updating Cloudflare DNS A and AAAA records, designed for dynamic IP environments such as home networks using Fritz!Box routers. Run it easily as a Docker container for reliable dynamic DNS (DDNS) updates.

**Example:**

```
CLOUDFLARE_DNS_HOSTNAMES=example.com,www.example.com
```
This will update the A and AAAA records for `@` in zone `example.com` and for `www` in zone `example.com`.

---

## Features

- Updates Cloudflare DNS A (IPv4) and AAAA (IPv6) records automatically
- Designed for dynamic IP scenarios (e.g., home routers)
- Supports IPv6 prefix delegation (IPv6 LAN prefix + host part)
- Runs as a minimal Docker container
- Compatible with FRITZ!Box custom Dynamic DNS

---

## Environment Variables

| Variable                | Required | Description                                                        |
|-------------------------|----------|--------------------------------------------------------------------|
| `CLOUDFLARE_API_TOKEN`  | Yes      | Cloudflare API token with DNS edit permissions                     |
| `CLOUDFLARE_DNS_HOSTNAMES` | Yes      | Comma-separated list of hostnames/subdomains to update A (IPv4) and AAAA (IPv6) records.  |

---

## How it Works

This script exposes a simple HTTP API endpoint (`/update`) that can be called by your FRITZ!Box (or any DDNS client) to update DNS records in Cloudflare:
- For each hostname in `CLOUDFLARE_DNS_HOSTNAMES`, it updates the A record (IPv4) and/or AAAA record (IPv6) as requested.
- For IPv6, you can provide either the full address or split it into a prefix (`ipv6lanprefix`) and a host part (`ipv6`). The script will combine them to form the complete IPv6 address.
- The response is a plain text status string (e.g., `good`, `nochg`, `badauth`, etc.) as expected by FRITZ!Box.

---

## Using with FRITZ!Box

You can use this script as a custom Dynamic DNS provider in your FRITZ!Box. Here’s how:

### 1. Expose the Service
- Make sure your fritzflare-dyndns instance is reachable from your FRITZ!Box (e.g., via local network or port forwarding).
- Note the URL and port (e.g., `http://192.168.178.2:8080/update`).

### 2. Configure FRITZ!Box Dynamic DNS
- Go to **Internet > Permit Access > Dynamic DNS** in the FRITZ!Box web interface.
- Select **User-defined provider**.
- Enter the following for the update URL:

  ```
  http://<host>:<port>/update?ipv4=<ipaddr>&ipv6lanprefix=<ip6lanprefix>&ipv6=<ip6addr>
  ```
  - `<host>`: The IP or hostname of your fritzflare-dyndns instance
  - `<port>`: The port you exposed (default: 8080)
  - `<ipaddr>`: The current IPv4 address (FRITZ!Box will substitute this automatically)
  - `<ip6lanprefix>`: The current IPv6 LAN prefix (FRITZ!Box will substitute this automatically)
  - `<ip6addr>`: The host part (IID) of your router’s IPv6 address (FRITZ!Box will substitute this automatically)

- Example:
  ```
  http://192.168.178.2:8080/update?ipv4=<ipaddr>&ipv6lanprefix=<ip6lanprefix>&ipv6=<ip6addr>
  ```
- Leave username and password blank (unless you add authentication).

### 3. Supported Parameters

| Property         | Supported Names in URL      | FRITZ!Box Placeholder in URL | Example Value                  |
|-----------------|----------------------------|------------------------------|-------------------------------|
| IPv4 Address    | ipv4, ip, myip, ipv4addr   | `<ipaddr>`                   | 203.0.113.42                  |
| IPv6 Address    | ipv6, myip, ipv6addr       | `<ip6addr>`                  | 2001:db8:abcd:1234::1         |
| IPv6 LAN Prefix | ipv6lanprefix, lanprefix   | `<ip6lanprefix>`             | 2001:db8:abcd:1234::/64       |

- Only the following parameters are supported by the `/update` route:
    - `ipv4` (IPv4 address)
    - `ipv6` (host part or full IPv6 address)
    - `ipv6lanprefix` (IPv6 LAN prefix)

### 4. Response Codes
- `good`: Update successful.
- `nochg`: No change needed (already up to date).
- `nohost`: Hostname not found or misconfigured.
- `badauth`: Authentication failed (if enabled).
- `badagent`: Malformed request or invalid IP.
- `911`: Server error, try again later.

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
