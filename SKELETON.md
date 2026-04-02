# Skeleton Management

This project was created from a reusable skeleton template. This file explains how to keep the skeleton in sync across projects.

## Setup

When you clone the skeleton to start a new project, keep a link to the skeleton repo as a second remote:

```bash
git clone <skeleton-repo-url> my-new-project
cd my-new-project
git remote rename origin skeleton
git remote add origin <your-project-repo-url>
git push -u origin main
```

Now your project has two remotes:
- `origin`: your project repo (where all your work goes)
- `skeleton`: the template repo (for backporting improvements)

## Improving the Skeleton During a Project

When you improve something generic (a `Makefile` tweak, a better template, a new helper), you can push it back to the skeleton so other projects benefit:

```bash
git add AGENTS.md
make skeleton-sync msg="add rule about figure naming convention"
```

This commits the staged files with a `[skeleton]` prefix and, if the `skeleton` remote exists, cherry-picks the commit and pushes it there. If no `skeleton` remote is configured, it just commits locally.

The AI agent follows this same workflow when it modifies skeleton files.

## Pulling Skeleton Updates

To pull improvements from the skeleton into a running project:

```bash
git fetch skeleton
git merge skeleton/main --allow-unrelated-histories
```

Resolve conflicts if needed.
