package main

import (
	"bytes"
	"strings"
	"testing"
)

func TestVersion(t *testing.T) {
	var out, errb bytes.Buffer
	if code := run([]string{"version"}, &out, &errb); code != exitOK {
		t.Fatalf("exit = %d, stderr = %q", code, errb.String())
	}
	if !strings.HasPrefix(out.String(), "outfit ") {
		t.Fatalf("unexpected output %q", out.String())
	}
}

func TestUnknownCommand(t *testing.T) {
	var out, errb bytes.Buffer
	if code := run([]string{"nope"}, &out, &errb); code != exitUsage {
		t.Fatalf("exit = %d, want %d", code, exitUsage)
	}
	if !strings.Contains(errb.String(), "unknown command") {
		t.Fatalf("stderr = %q", errb.String())
	}
}

func TestNoArgs(t *testing.T) {
	var out, errb bytes.Buffer
	if code := run(nil, &out, &errb); code != exitUsage {
		t.Fatalf("exit = %d, want %d", code, exitUsage)
	}
}
