# Complete Guide: Removing "/odoo" from URL in Odoo Enterprise On-Premise with Nginx

This comprehensive guide explains how to remove the `/odoo` path from your Odoo Enterprise On-Premise installation URL using Nginx as a reverse proxy. This is the **standard, production-ready method** used by thousands of Odoo deployments worldwide.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Understanding the Problem](#understanding-the-problem)
3. [Why Nginx + Odoo Configuration Works](#why-nginx--odoo-configuration-works)
4. [Step-by-Step Implementation](#step-by-step-implementation)
   - [Step 1: Install Nginx](#step-1-install-nginx)
   - [Step 2: Configure Odoo](#step-2-configure-odoo)
   - [Step 3: Configure Nginx](#step-3-configure-nginx)
   - [Step 4: Test and Apply Configuration](#step-4-test-and-apply-configuration)
   - [Step 5: Clear Browser Cache](#step-5-clear-browser-cache)
5. [Troubleshooting Common Issues](#troubleshooting-common-issues)
6. [Verification Checklist](#verification-checklist)
7. [Security Considerations](#security-considerations)

---

## Prerequisites

Before starting, ensure you have:

- **Odoo Enterprise On-Premise** installed and running (typically on port 8069)
- **Root or sudo access** to your server
- **Ubuntu/Debian** or similar Linux distribution (commands may vary slightly for other distros)
- Odoo currently accessible at `http://<SERVER_IP>:8069` or `http://<SERVER_IP>/odoo`
- No other service running on port 80

---

## Understanding the Problem

By default, Odoo runs on port 8069 and serves content at paths like:
- `http://your-server-ip:8069/web/login`
- `http://your-server-ip/odoo/web/login` (if behind a basic proxy)

The goal is to make Odoo accessible at:
- `http://your-server-ip/web/login` (no `/odoo` prefix)
- `http://your-domain.com/web/login` (if you have a domain)

**Why doesn't simple URL rewriting work?**

Odoo generates internal links, redirects, and static asset URLs dynamically. If Odoo doesn't know it's behind a proxy serving content at the root path, it will continue generating URLs with `/odoo` or `:8069`, breaking navigation, logins, and asset loading.

---

## Why Nginx + Odoo Configuration Works

The solution requires **two components working together**:

### 1. **Nginx Reverse Proxy**
- Forwards all requests from port 80 to Odoo's port 8069
- Adds special headers to tell Odoo about the original request
- Handles static files efficiently

### 2. **Odoo Proxy Mode**
- When `proxy_mode = True`, Odoo reads the forwarded headers
- Odoo understands it's behind a proxy and generates correct URLs
- Odoo adapts its internal URL generation to match the external path

**Key Headers:**
- `X-Real-IP`: Original client IP
- `X-Forwarded-For`: Chain of proxy IPs
- `X-Forwarded-Proto`: Original protocol (http/https)
- `X-Forwarded-Host`: Original hostname
- `Host`: Original host header

Without these headers, Odoo thinks it's running directly on port 8069 and generates incorrect URLs.

---

## Step-by-Step Implementation

### Step 1: Install Nginx

If Nginx is not already installed:

```bash
sudo apt update
sudo apt install nginx -y
```

Verify Nginx is running:

```bash
sudo systemctl status nginx
```

You should see `active (running)`. If not, start it:

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Step 2: Configure Odoo

Edit your Odoo configuration file. The location varies by installation:

**Common locations:**
- `/etc/odoo/odoo.conf`
- `/etc/odoo-server.conf`
- `/opt/odoo/odoo.conf`
- `~/.odoorc`

```bash
sudo nano /etc/odoo/odoo.conf
```

**Add or modify these settings in the `[options]` section:**

```ini
[options]
# Enable proxy mode - CRITICAL for URL rewriting
proxy_mode = True

# Bind Odoo to localhost only (security best practice)
http_interface = 127.0.0.1

# Ensure Odoo listens on port 8069
http_port = 8069

# DO NOT set http_script_name - this would break root path access
# Leave this commented out or remove it if present:
# http_script_name = /odoo
```

**Complete example odoo.conf:**

```ini
[options]
admin_passwd = your_admin_password
db_host = localhost
db_port = 5432
db_user = odoo
db_password = your_db_password
data_dir = /var/lib/odoo
logfile = /var/log/odoo/odoo.log
log_level = info

# Proxy configuration
proxy_mode = True
http_interface = 127.0.0.1
http_port = 8069

# Other settings
workers = 4
max_cron_threads = 1
limit_time_cpu = 60
limit_time_real = 120
```

**Save and exit** (Ctrl+X, then Y, then Enter in nano).

**Restart Odoo to apply changes:**

```bash
sudo systemctl restart odoo
# OR if you use a different service name:
# sudo systemctl restart odoo-server
# sudo service odoo restart
```

Verify Odoo is running and listening on localhost:

```bash
sudo systemctl status odoo
curl http://127.0.0.1:8069/web/login
```

You should see HTML output (the login page source).

### Step 3: Configure Nginx

Remove the default Nginx configuration:

```bash
sudo rm /etc/nginx/sites-enabled/default
```

Create a new Odoo configuration file:

```bash
sudo nano /etc/nginx/sites-available/odoo
```

**Paste the following complete configuration:**

```nginx
upstream odoo {
    server 127.0.0.1:8069;
}

upstream odoochat {
    server 127.0.0.1:8072;
}

server {
    listen 80;
    server_name _;

    # Logging
    access_log /var/log/nginx/odoo_access.log;
    error_log /var/log/nginx/odoo_error.log;

    # Main Odoo location
    location / {
        proxy_pass http://odoo;
        
        # Essential headers for Odoo proxy mode
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # WebSocket support (for live chat, notifications)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts for long operations
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        
        # Buffering settings
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # Static files caching (optional optimization)
    location ~* /web/static/ {
        proxy_pass http://odoo;
        proxy_cache_valid 200 60m;
        proxy_buffering on;
        expires 30d;
        add_header Cache-Control "public, immutable";
        
        # Still send headers for Odoo to generate correct URLs
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
    }

    # Longpolling/chat (if using separate port 8072)
    location /longpolling {
        proxy_pass http://odoochat;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_min_length 1000;
}
```

**Save and exit** (Ctrl+X, then Y, then Enter).

**Enable the site:**

```bash
sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/odoo
```

### Step 4: Test and Apply Configuration

**Test Nginx configuration for syntax errors:**

```bash
sudo nginx -t
```

Expected output:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

If you see errors, fix them before proceeding.

**Reload Nginx to apply changes:**

```bash
sudo systemctl reload nginx
```

**Verify both services are running:**

```bash
sudo systemctl status nginx
sudo systemctl status odoo
```

Both should show `active (running)`.

### Step 5: Clear Browser Cache

**This step is critical!** Your browser may have cached old URLs with `/odoo` or port 8069.

**Options to clear cache:**

1. **Hard refresh**: Press `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
2. **Clear browser cache completely**: Go to browser settings and clear cached images/files
3. **Use incognito/private mode**: Open a new incognito window
4. **Clear from command line** (if testing with curl):
   ```bash
   curl -L http://YOUR_SERVER_IP/web/login
   ```

**Access Odoo at the new URL:**

```
http://YOUR_SERVER_IP/web/login
```

Or if you have a domain:
```
http://your-domain.com/web/login
```

**Do NOT use:**
- `http://YOUR_SERVER_IP/odoo` (old path)
- `http://YOUR_SERVER_IP:8069` (direct port access should be blocked by firewall)

---

## Troubleshooting Common Issues

### Issue 1: "Redirect Loop" or Infinite Redirects

**Symptoms:** Browser shows "Too many redirects" error.

**Causes:**
- `proxy_mode = True` not set in odoo.conf
- Missing `X-Forwarded-Proto` header in Nginx
- Odoo not restarted after config change

**Solution:**
```bash
# Verify odoo.conf has proxy_mode = True
grep "proxy_mode" /etc/odoo/odoo.conf

# Verify Nginx config has X-Forwarded-Proto
grep "X-Forwarded-Proto" /etc/nginx/sites-available/odoo

# Restart both services
sudo systemctl restart odoo
sudo systemctl reload nginx

# Clear browser cache completely
```

### Issue 2: Login Works but Internal Links Broken

**Symptoms:** You can log in, but clicking menus redirects to wrong URLs or shows 404.

**Causes:**
- Missing `X-Forwarded-Host` header
- `http_script_name` set in odoo.conf
- Browser cache still has old URLs

**Solution:**
```bash
# Remove http_script_name from odoo.conf if present
sudo nano /etc/odoo/odoo.conf
# Comment out or delete any line with http_script_name

# Ensure X-Forwarded-Host is in Nginx config
grep "X-Forwarded-Host" /etc/nginx/sites-available/odoo

# Restart services
sudo systemctl restart odoo
sudo systemctl reload nginx

# Clear browser cache and try incognito mode
```

### Issue 3: Static Assets (CSS/JS) Not Loading

**Symptoms:** Page loads but looks broken, missing styles, console shows 404 for static files.

**Causes:**
- Static file location block missing in Nginx
- Wrong proxy_pass for static files
- Caching issues

**Solution:**
```bash
# Ensure static location block exists in Nginx config
grep -A 10 "/web/static/" /etc/nginx/sites-available/odoo

# Check Nginx error logs
sudo tail -f /var/log/nginx/odoo_error.log

# Reload Nginx
sudo systemctl reload nginx

# Hard refresh browser (Ctrl+Shift+R)
```

### Issue 4: WebSocket/Chat Not Working

**Symptoms:** Live chat, notifications, or real-time updates don't work.

**Causes:**
- Missing WebSocket upgrade headers
- Longpolling service not configured
- Timeout too short

**Solution:**
```bash
# Ensure these lines are in Nginx config:
# proxy_http_version 1.1;
# proxy_set_header Upgrade $http_upgrade;
# proxy_set_header Connection "upgrade";

# If using longpolling on port 8072, ensure that upstream is configured

# Increase timeouts
sudo nano /etc/nginx/sites-available/odoo
# Set proxy_read_timeout 86400; for longpolling location

sudo systemctl reload nginx
```

### Issue 5: 502 Bad Gateway Error

**Symptoms:** Nginx returns 502 error.

**Causes:**
- Odoo service not running
- Odoo not listening on 127.0.0.1:8069
- Firewall blocking localhost connection

**Solution:**
```bash
# Check if Odoo is running
sudo systemctl status odoo

# Check if Odoo is listening on correct port
sudo netstat -tlnp | grep 8069
# or
sudo ss -tlnp | grep 8069

# Check Odoo logs for errors
sudo tail -f /var/log/odoo/odoo.log

# Test direct connection
curl http://127.0.0.1:8069/web/login

# If not listening, check odoo.conf http_interface setting
grep "http_interface" /etc/odoo/odoo.conf
# Should be: http_interface = 127.0.0.1
```

### Issue 6: Still Shows /odoo in Address Bar After Login

**Symptoms:** Initial login works at root, but after login URL changes to include `/odoo`.

**Causes:**
- Database or system parameter caching old base URL
- `proxy_mode` was False when database was initialized
- Browser cache

**Solution:**
```bash
# Update web.base.url in database (via Odoo shell or UI)
# Method 1: Via Odoo UI (if you can access debug mode)
# Settings > Technical > Parameters > System Parameters
# Find 'web.base.url' and update to http://YOUR_SERVER_IP

# Method 2: Via command line
sudo su - odoo -s /bin/bash
odoo-bin shell -d YOUR_DATABASE_NAME --load=web
>>> env['ir.config_parameter'].set_param('web.base.url', 'http://YOUR_SERVER_IP')
>>> exit()

# Restart Odoo
sudo systemctl restart odoo

# Clear browser cache completely and logout/login again
```

---

## Verification Checklist

After implementation, verify each item:

- [ ] Nginx is running: `sudo systemctl status nginx`
- [ ] Odoo is running: `sudo systemctl status odoo`
- [ ] Nginx config test passes: `sudo nginx -t`
- [ ] `proxy_mode = True` in odoo.conf
- [ ] `http_interface = 127.0.0.1` in odoo.conf
- [ ] No `http_script_name` in odoo.conf
- [ ] Nginx config includes all required headers:
  - [ ] `X-Real-IP`
  - [ ] `X-Forwarded-For`
  - [ ] `X-Forwarded-Proto`
  - [ ] `X-Forwarded-Host`
  - [ ] `X-Forwarded-Port`
- [ ] WebSocket headers present (`Upgrade`, `Connection`)
- [ ] Can access login page at `http://SERVER_IP/web/login`
- [ ] No `/odoo` in address bar
- [ ] Login successful
- [ ] All menu items work without 404 errors
- [ ] Static assets (CSS/JS/images) load correctly
- [ ] No redirect loops
- [ ] Browser cache cleared
- [ ] Direct port 8069 access blocked by firewall (optional security)

**Quick verification commands:**

```bash
# Test login page
curl -I http://YOUR_SERVER_IP/web/login

# Should return HTTP/1.1 200 OK, not 301/302 redirect to /odoo

# Check if Odoo is only listening on localhost
sudo ss -tlnp | grep 8069
# Should show 127.0.0.1:8069, not 0.0.0.0:8069

# Check Nginx is listening on port 80
sudo ss -tlnp | grep :80
# Should show 0.0.0.0:80 or :::80
```

---

## Security Considerations

### 1. Block Direct Port 8069 Access

Prevent users from bypassing Nginx by accessing Odoo directly on port 8069:

```bash
# Configure firewall (UFW example)
sudo ufw deny 8069/tcp
sudo ufw allow 80/tcp
sudo ufw reload

# Or with iptables
sudo iptables -A INPUT -p tcp --dport 8069 -s 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8069 -j DROP
```

### 2. Restrict Odoo to Localhost

Ensure `http_interface = 127.0.0.1` in odoo.conf so Odoo only accepts connections from Nginx on the same server.

### 3. Add Rate Limiting (Optional)

Prevent brute force attacks:

```nginx
# Add to nginx config, inside server block
limit_req_zone $binary_remote_addr zone=odoo_limit:10m rate=10r/s;

location / {
    limit_req zone=odoo_limit burst=20 nodelay;
    # ... rest of proxy config
}
```

### 4. Enable HTTPS (Recommended for Production)

While this guide covers HTTP, for production you should enable HTTPS:

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Update odoo.conf for HTTPS
# proxy_mode = True (already set)
# In Odoo UI: Settings > General Settings > Base URL -> https://your-domain.com
```

### 5. Hide Odoo Version

Add to Nginx config to hide version information:

```nginx
server_tokens off;
```

---

## Summary

You have successfully configured Odoo Enterprise On-Premise to run without the `/odoo` prefix in the URL. This setup:

✅ Uses industry-standard Nginx reverse proxy  
✅ Requires no custom Odoo modules  
✅ Survives Odoo upgrades  
✅ Maintains all Odoo functionality  
✅ Follows Odoo SA's recommended deployment pattern  

**Key success factors:**
1. `proxy_mode = True` in odoo.conf
2. All required X-Forwarded-* headers in Nginx
3. No `http_script_name` configuration
4. Complete browser cache clearing
5. Both services properly restarted

If you encounter issues, refer to the [Troubleshooting](#troubleshooting-common-issues) section above.

---

## Additional Resources

- [Official Odoo Documentation - Proxy Mode](https://www.odoo.com/documentation/)
- [Nginx Reverse Proxy Best Practices](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Odoo Deployment Guidelines](https://www.odoo.com/documentation/administration/deployment/)

---

**License:** This guide is provided as-is for educational purposes.  
**Version:** 1.0  
**Last Updated:** 2024
