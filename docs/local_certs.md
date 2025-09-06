# Local SSL Certificates

This directory contains SSL certificates for local development purposes.

> They expire on 8 August 2027 🗓

The `localhost.pem` and `localhost-key.pem` files are used to enable HTTPS for the local development server.
This is necessary when working with OAuth 2.0 providers that require secure redirect URIs.

## Generating Certificates
These were created with mkcert, a simple tool for making locally-trusted development certificates.

1.  **Install `mkcert`**: Follow the instructions for your operating system from the [mkcert GitHub repository](https://github.com/FiloSottile/mkcert).
2.  **Install a local CA (Certificate Authority)**:
    ```bash
    mkcert -install
    ```
    This command installs a local CA in your system's trust stores. You only need to do this once.
3.  **Generate certificates for `localhost`**:
    ```bash
    mkcert localhost
    ```
    This will create `localhost.pem` (certificate) and `localhost-key.pem` (private key) in the current directory.
    You can then move them to the `certs` directory.
4.  **Use the certificates**: When running your local development server, configure it to use these certificates for HTTPS.