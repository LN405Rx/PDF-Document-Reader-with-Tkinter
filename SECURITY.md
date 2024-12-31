# Security Policy

## Supported Versions

Currently being supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within this project:

1. **Do Not** open a public issue
2. Send a private message to the repository maintainer
3. Include detailed steps to reproduce the vulnerability
4. Allow some time for the vulnerability to be addressed before public disclosure

## Security Considerations

This application:
- Does not collect or transmit personal data
- Processes PDF files locally only
- Stores audio output files locally
- Uses environment variables for configuration
- Implements file access restrictions

## Best Practices for Users

1. Never share your `.env` file
2. Keep your dependencies updated
3. Don't process sensitive PDF documents
4. Regularly clean up output directories
5. Use the latest stable version
