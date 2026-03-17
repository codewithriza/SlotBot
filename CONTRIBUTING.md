# Contributing to SlotBot

Thank you for your interest in contributing to SlotBot! 🎰

## How to Contribute

### Reporting Bugs

1. Check the [existing issues](https://github.com/codewithriza/SlotBot/issues) to avoid duplicates.
2. Open a new issue with a clear title and description.
3. Include steps to reproduce the bug.
4. Add relevant logs from `slotbot.log` if applicable.

### Suggesting Features

1. Open an issue with the `enhancement` label.
2. Describe the feature and why it would be useful.
3. If possible, include mockups or examples.

### Submitting Code

1. **Fork** the repository.
2. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```
3. **Make your changes** and test them thoroughly.
4. **Commit** with clear, descriptive messages:
   ```bash
   git commit -m "feat: add slot transfer command"
   ```
5. **Push** to your fork:
   ```bash
   git push origin feature/my-awesome-feature
   ```
6. **Open a Pull Request** against the `main` branch.

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix   | Description                          |
|----------|--------------------------------------|
| `feat:`  | A new feature                        |
| `fix:`   | A bug fix                            |
| `docs:`  | Documentation changes                |
| `style:` | Code style (formatting, no logic)    |
| `refactor:` | Code refactoring                  |
| `test:`  | Adding or updating tests             |
| `chore:` | Maintenance tasks                    |

### Code Style

- Use **Python 3.10+** features.
- Follow **PEP 8** conventions.
- Add docstrings to all functions and commands.
- Use type hints where possible.
- Keep functions focused and small.

### Testing

Before submitting a PR, make sure:

- [ ] The bot starts without errors.
- [ ] All commands work as expected.
- [ ] No hardcoded IDs are present (use `config.json`).
- [ ] Error handling is in place for edge cases.

## Code of Conduct

- Be respectful and constructive.
- Help others learn and grow.
- No spam, harassment, or off-topic discussions.

## Need Help?

- Join our [Discord server](https://discord.gg/JdyvFVgsTN)
- Open an [issue](https://github.com/codewithriza/SlotBot/issues)
- Contact [@codewithriza](https://discord.com/users/887532157747212370)

---

Thank you for helping make SlotBot better! 🚀
