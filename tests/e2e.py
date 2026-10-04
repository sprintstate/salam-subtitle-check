"""Black-box checks of the compiled CLI; needs only Python's standard library."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


EXE = Path(sys.argv[1]).resolve()
ROOT = Path(__file__).resolve().parents[1]
checks = 0


def run(*args, expected=0, report=True, cwd=None):
    global checks
    result = subprocess.run(
        [str(EXE), *map(str, args)], capture_output=True, timeout=15, cwd=cwd
    )
    assert result.returncode == expected, (args, result.returncode, result.stderr, result.stdout)
    if report:
        assert result.stderr == b"", result.stderr
        data = json.loads(result.stdout)
        assert data["schema_version"] == 1
        assert data["exit_code"] == expected
    else:
        data = result
    checks += 1
    return data


def codes(data):
    return {item["code"] for item in data["diagnostics"]}


def main():
    clean = ROOT / "examples/clean.srt"
    warnings = ROOT / "examples/warnings.srt"
    invalid = ROOT / "examples/invalid.srt"
    assert run("--json", clean)["diagnostics"] == []
    assert run("--json", "--strict", clean)["cues"] == 2
    assert codes(run("--json", warnings)) == {
        "W_SEQUENCE", "W_SHORT", "W_OVERLAP", "W_WIDTH", "W_CPS"
    }
    run("--json", "--strict", warnings, expected=1)
    assert codes(run("--json", invalid, expected=1)) == {"E_DURATION", "E_TIMESTAMP"}
    assert b"Checked 2 cues: 0 errors, 0 warnings." in run(clean, report=False).stdout
    assert b"Usage:" in run("--help", report=False).stdout
    for args in [[], ["--unknown"], ["--max-cps"], ["--max-cps", "0"],
                 ["--max-line", "1001"], ["--max-line", "1x"], [clean, clean]]:
        assert "fatal" in run("--json", *args, expected=2)
    run("--json", ROOT / "no-such-file.srt", expected=2)
    run("--json", ROOT / "examples", expected=2)
    content = "1\n00:00:00,000 --> 00:00:01,000\nПривет世界🙂\n"
    with tempfile.TemporaryDirectory(prefix="salam subtitles ") as temporary:
        folder = Path(temporary)
        path = folder / "субтитры 世界.srt"
        for newline in ["\n", "\r\n", "\r"]:
            for bom in [b"", b"\xef\xbb\xbf"]:
                payload = bom + content.replace("\n", newline).encode("utf-8")
                path.write_bytes(payload)
                before = hashlib.sha256(path.read_bytes()).digest()
                data = run("--json", "--max-cps", "9", "--max-line", "9", path)
                assert data["file"] == str(path)
                assert data["diagnostics"] == []
                assert hashlib.sha256(path.read_bytes()).digest() == before
        path.write_bytes(content.encode("utf-8"))
        assert codes(run("--json", "--max-cps", "8", path)) == {"W_CPS"}
        prefix = b"1\n00:00:00,000 --> 00:00:01,000\n"
        for suffix in [b"\xc0\xaf", b"\x80", b"\xed\xa0\x80", b"\xf4\x90\x80\x80",
                       b"\xf5\x80\x80\x80", b"\xe2\x82", b"\xc2A", b"\x1b", b"\x7f", b"a\0b"]:
            path.write_bytes(prefix + suffix)
            assert "fatal" in run("--json", path, expected=2)
        path.write_bytes(content.encode("utf-16"))
        run("--json", path, expected=2)
        path.write_bytes(b"")
        assert codes(run("--json", path, expected=1)) == {"E_EMPTY"}
        path.write_bytes(prefix + b"x" * (1048576 - len(prefix)))
        assert run("--json", path)["cues"] == 1
        path.write_bytes(b"x" * 1048577)
        run("--json", path, expected=2)
        path.write_bytes(b"1\nwrong\ntext\n\n2\n00:00:01,000 --> 00:00:02,000\nFine")
        data = run("--json", path, expected=1)
        assert data["cues"] == 1
        assert data["diagnostics"][0]["line"] == 2
        dash = folder / "-file.srt"
        dash.write_bytes(content.encode("utf-8"))
        run("--json", "--", "-file.srt", cwd=folder)
    print(f"{checks} end-to-end cases passed")


if __name__ == "__main__":
    main()
