"""CLI commands for encryption management."""

import click
from envswitch.encrypt import (
    generate_key, save_key, load_key, encrypt_profile,
    decrypt_profile, is_encrypted, EncryptionError,
    get_key_path
)
from envswitch.storage import load_profiles, save_profiles, get_profile


@click.group("encrypt")
def encrypt_cmd():
    """Manage encryption for profile values."""


@encrypt_cmd.command("init")
@click.option("--force", is_flag=True, help="Overwrite existing key")
def enc_init(force):
    """Generate a new encryption key."""
    path = get_key_path()
    if path.exists() and not force:
        click.echo(f"Key already exists at {path}. Use --force to overwrite.", err=True)
        raise SystemExit(1)
    key = generate_key()
    save_key(key)
    click.echo(f"Encryption key saved to {path}")


@encrypt_cmd.command("encrypt")
@click.argument("profile")
@click.option("--var", multiple=True, help="Specific vars to encrypt (default: all)")
def enc_encrypt(profile, var):
    """Encrypt values in a profile."""
    try:
        key = load_key()
    except EncryptionError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    profiles = load_profiles()
    if profile not in profiles:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    vars_to_encrypt = list(var) if var else None
    profiles[profile] = encrypt_profile(profiles[profile], key, vars_to_encrypt)
    save_profiles(profiles)
    click.echo(f"Profile '{profile}' encrypted.")


@encrypt_cmd.command("decrypt")
@click.argument("profile")
def enc_decrypt(profile):
    """Decrypt and show values in a profile."""
    try:
        key = load_key()
    except EncryptionError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    profiles = load_profiles()
    if profile not in profiles:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    try:
        decrypted = decrypt_profile(profiles[profile], key)
    except EncryptionError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    for k, v in decrypted.items():
        click.echo(f"{k}={v}")


@encrypt_cmd.command("status")
@click.argument("profile")
def enc_status(profile):
    """Show encryption status of each var in a profile."""
    profiles = load_profiles()
    if profile not in profiles:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    for k, v in profiles[profile].items():
        status = "[encrypted]" if is_encrypted(v) else "[plaintext]"
        click.echo(f"{k}: {status}")
