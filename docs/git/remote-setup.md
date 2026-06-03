# Git Remote Setup

The repository is initialized locally, but no remote is configured.

Check the current state:

```bash
git remote -v
git log --oneline --decorate -5
```

After creating an empty GitLab or GitHub repository, attach it:

```bash
git remote add origin <REPOSITORY_SSH_OR_HTTPS_URL>
git push -u origin main
```

If `origin` already points to GitLab and GitHub should be an additional remote:

```bash
git remote add github https://github.com/Pernya/prizma.git
git push -u github main
```

For GitLab CI/CD, configure these project variables before relying on deploy jobs:

- `KUBECONFIG_DEV`
- `KUBECONFIG_PROD`
- `CI_REGISTRY_USER`
- `CI_REGISTRY_PASSWORD`

The chart production profiles expect a Kubernetes Secret named `prizma-runtime-overrides`
or an ExternalSecret-backed Secret with the same keys.

## GitHub Actions CD

The GitHub CI workflow pushes backend images to GitHub Container Registry:

```text
ghcr.io/pernya/prizma-backend:<commit-sha>
ghcr.io/pernya/prizma-backend:latest
```

Manual deployment uses `.github/workflows/deploy.yml`.

Configure a GitHub Environment named `dev`, `regcloud` or `prod`, then add this secret:

- `KUBECONFIG_B64`: base64-encoded kubeconfig for the target cluster

Make the GHCR package public or add an image pull secret to the target cluster before deploying.

Encode kubeconfig locally:

```bash
base64 -i ~/.kube/config | pbcopy
```

Run deployment in GitHub:

```text
Actions -> Deploy -> Run workflow
```

## GitHub Actions VPS CD

The current public server mode uses Docker Compose on the VPS and does not require Kubernetes.

Workflow:

```text
Actions -> Deploy VPS Frontend -> Run workflow
```

Create a GitHub Environment named `vps`, then add these environment secrets:

- `VPS_HOST`: public server IP or hostname, for example `194.226.142.176`
- `VPS_PORT`: SSH port, usually `22`
- `VPS_USER`: SSH user, for example `root`
- `VPS_SSH_KEY`: private SSH key allowed to connect to the VPS
- `VPS_APP_DIR`: target directory, for example `/opt/prizma/frontend`

The workflow uploads only the public frontend bundle and runs:

```bash
docker compose -f docker-compose.frontend-server.yml -p prizma-frontend up -d
```
