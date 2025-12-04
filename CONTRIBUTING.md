# Contributing Guide

Thank you for considering contributing to `sparqlx`!

This document outlines how to participate constructively.
Please read these guidelines before opening Issues or Pull Requests.


<!-- omit in toc -->
## Table of Contents

- [Vision](#vision)
- [I Have a Question](#i-have-a-question)
- [Styleguide](#styleguide)
- [Issues-Before-Pull-Requests Policy](#issues-before-pull-requests-policy)
- [Git/Github Workflow](#gitgithub-workflow)
- [Anti-AI-Slop Policy](#anti-ai-slop-policy)

## Vision

`sparqlx` aims to be a modern Sync/Async SPARQL 1.2 Protocol client based on `httpx`.

The library should be as simple as possible but no simpler.

This means e.g. that

- `sparqlx` should do one thing well; i.e. the library shall provide solid core functionality and beyond that will prefer recipes and usage patterns over features

- the implementation should be guided primarily by the [SPARQL 1.2 Protocol specification](https://www.w3.org/TR/sparql12-protocol/)

- the library API aims to be simple and [deep](https://vladimirzdrazil.com/posts/deep-shallow-modules/)

## I Have a Question

> If you want to ask a question, we assume that you have read at least the README.

Before you ask a question, it is best to search for existing [Issues](https://github.com/lu-pl/sparqlx/issues) that might help you. In case you have found a suitable issue and still need clarification, you can write your question in this issue. It is also advisable to search the internet for answers first.

If you then still feel the need to ask a question and need clarification, we recommend the following:

- Open an [Issue](https://github.com/lu-pl/sparqlx/issues/new).
- Provide as much context as you can about what you're running into.
- Provide project and platform versions (nodejs, npm, etc), depending on what seems relevant.

We will then take care of the issue as soon as possible.

## Styleguide

### General

Please try to keep your commit changes focused on the change you want to implement - don't start fixing typos if your commit is actually about adding a feature.

`sparqlx` uses [ruff](https://docs.astral.sh/ruff/) for linting and code formatting.

`sparqlx` also uses the [deptry](https://deptry.com/) dependency checker for detecting missing or unused dependencies.

### Commit Messages

`sparqlx` uses [conventional commits](https://www.conventionalcommits.org/) so please format your commit messages accordingly.
The `sparqlx` repo runs a GitHub Action that uses the [Gitlint](https://github.com/jorisroovers/gitlint) linter to check commit messages for validity.

Consider using a scope when writing a commit message. See [Commit message with scope](https://www.conventionalcommits.org/en/v1.0.0/#commit-message-with-scope).


## Issues-Before-Pull-Requests Policy

To keep the project focused, maintainable, and aligned with its vision, `sparqlx` follows an Issue-first workflow.

> All PRs should reference an existing issue.

If you want to propose a change - whether it’s a bug fix, refactor, feature, or documentation update - please follow this process:

1. Open an Issue describing the problem/motivation/rationale and (optionally) a proposed approach towards Issue resolution.

> Issues must be narrow in scope and focus on a single topic.

2. Wait for maintainers to acknowledge or discuss the proposal.

Discussion should happen on the Issue and confirm scope, direction, and/or alternatives.

3. Only after the Issue is acknowledged, open a Pull Request that explicitly references it

> Pull Requests must be narrow in scope and focus on a single topic.


## Git/Github Workflow

`sparqlx` uses a rebase workflow to keep history clean.

Please:

- Base your branch off the latest main

- Avoid merge commits in feature branches

- Ensure each commit is logically focused


## Anti-AI-Slop Policy

This project values clarity, maintainability, and human intent in contributions.

> Submissions that appear to be AI output may be closed without review.

Please be a good Homo Sapiens and use your brain.
