# Contributing to UNT Mental Health Analysis

Thank you for your interest in contributing to this project! This document provides guidelines for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Respect privacy and data sensitivity
- Follow ethical guidelines for data analysis

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion:

1. Check if the issue already exists
2. Create a new issue with a clear description
3. Include steps to reproduce (for bugs)
4. Add relevant labels

### Submitting Changes

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/unt-mental-health-analysis.git
   cd unt-mental-health-analysis
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clear, documented code
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```bash
   pytest tests/
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: clear description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure all tests pass

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

### Testing

- Write unit tests for new functions
- Maintain test coverage above 80%
- Test edge cases and error handling

### Documentation

- Update README.md for significant changes
- Document new features and APIs
- Include examples in docstrings

### Data Privacy

- Never commit real student data
- Use anonymized sample data only
- Follow FERPA and HIPAA guidelines
- Remove any PII before committing

## Project Structure

```
unt-mental-health-analysis/
├── src/              # Source code
├── tests/            # Unit tests
├── notebooks/        # Jupyter notebooks
├── data/             # Data files (not committed)
├── config/           # Configuration files
└── docs/             # Documentation
```

## Getting Help

- Check existing issues and documentation
- Ask questions in GitHub Discussions
- Contact maintainers for major changes

## Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing!
