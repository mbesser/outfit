// Command outfit runs a git monorepo under a profile: which hook checks run,
// and a few swapped files. See docs/HANDOVER.md for the spec.
package main

import (
	"fmt"
	"io"
	"os"
	"os/exec"
	"runtime"
	"strings"
)

// Set by the release build through -ldflags; "dev" marks a local build.
var (
	version = "dev"
	commit  = "none"
	date    = "unknown"
)

const (
	exitOK    = 0
	exitUsage = 2
)

func main() {
	os.Exit(run(os.Args[1:], os.Stdout, os.Stderr))
}

func run(args []string, stdout, stderr io.Writer) int {
	if len(args) == 0 {
		fmt.Fprintln(stderr, "usage: outfit <command>\nrun `outfit version` to see the installed version")
		return exitUsage
	}
	switch args[0] {
	case "version":
		fmt.Fprintf(stdout, "outfit %s (commit %s, built %s, %s/%s, git %s)\n",
			version, commit, date, runtime.GOOS, runtime.GOARCH, gitVersion())
		return exitOK
	default:
		fmt.Fprintf(stderr, "outfit: unknown command %q\nrun `outfit version`; more commands arrive with later releases\n", args[0])
		return exitUsage
	}
}

// gitVersion reports the git on PATH, or "not found". The full floor check
// (git >= 2.36) arrives with internal/gitx.
func gitVersion() string {
	out, err := exec.Command("git", "--version").Output()
	if err != nil {
		return "not found"
	}
	return strings.TrimPrefix(strings.TrimSpace(string(out)), "git version ")
}
