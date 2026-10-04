# Salam Subtitle Check

An offline SRT subtitle validator built with the
[Salam Programming Language](https://github.com/SalamLang/Salam).

The application is under development. The first milestone provides strict
timestamp parsing and typed subtitle/diagnostic records. It uses Salam 0.4.8.

Build and run the native unit tests:

```text
salam build tests/unit.salam --backend=c --cc=gcc --output=build/unit
./build/unit
```

Create the `build` directory first. On Windows the output is `build/unit.exe`.
Development and testing use OpenAI Codex; no independent human technical review
is claimed.
