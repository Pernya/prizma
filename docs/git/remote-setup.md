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

For GitLab CI/CD, configure these project variables before relying on deploy jobs:

- `KUBECONFIG_DEV`
- `KUBECONFIG_PROD`
- `CI_REGISTRY_USER`
- `CI_REGISTRY_PASSWORD`

The chart production profiles expect a Kubernetes Secret named `prizma-runtime-overrides`
or an ExternalSecret-backed Secret with the same keys.
