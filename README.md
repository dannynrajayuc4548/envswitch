# envswitch

A CLI tool for quickly switching between named environment variable profiles across projects.

---

## Installation

```bash
pip install envswitch
```

Or install from source:

```bash
git clone https://github.com/yourname/envswitch.git && cd envswitch && pip install .
```

---

## Usage

**Create a profile:**
```bash
envswitch add staging API_URL=https://staging.example.com API_KEY=abc123
```

**Switch to a profile:**
```bash
envswitch use staging
```

**List available profiles:**
```bash
envswitch list
```

**Remove a profile:**
```bash
envswitch remove staging
```

Profiles are stored in `~/.envswitch/profiles.json` and can be scoped per project using a local `.envswitchrc` file.

---

## Example

```bash
$ envswitch add production DB_HOST=prod.db.example.com DB_PASS=supersecret
$ envswitch use production
✔ Switched to profile: production
```

---

## License

This project is licensed under the [MIT License](LICENSE).