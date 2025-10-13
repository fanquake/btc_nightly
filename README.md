# Nightly Bitcoin Core tests

This is a collection of nightly Bitcoin Core CI tests.

They are generally not suitable for integration into the main Bitcoin Core CI
config, as they are expected to break frequently. For example, a dependency,
such as a nightly compiler package or nightly container image may be buggy.

The goal is to find such bugs, report and fix them upstream, before they hit
real users, without plaguing the main CI with intermittent failures.
