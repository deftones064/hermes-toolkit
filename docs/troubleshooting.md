# Troubleshooting

## hermes-settings command not found

Run:

export PATH="/usr/local/bin:$PATH"

To make it permanent:

echo 'export PATH="/usr/local/bin:$PATH"' >> /root/.bashrc

## GitHub push fails

Use GitHub CLI:

gh auth login
git push
