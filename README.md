# outfit

Run a git monorepo under a **profile**: which hook checks run, and a few swapped
files (`AGENTS.md`, `CLAUDE.md`…). Your teammates never notice, and `git status`
stays truthful.

> **Status: bootstrapping.** The full spec is [docs/HANDOVER.md](docs/HANDOVER.md).
> Features land one PR at a time; this README gets its install one-liner and demo
> in the docs PR.

## Develop

Every change goes through the ship workflow: see [AGENTS.md](AGENTS.md) and
[docs/ship.md](docs/ship.md).

```sh
go build ./cmd/outfit && ./outfit version
gofmt -l . && go vet ./... && golangci-lint run && go test -race ./...
```

MIT licensed.
