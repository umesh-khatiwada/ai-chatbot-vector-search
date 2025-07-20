# Contributing to AI Chatbot Vector Search

Thank you for your interest in contributing to this project! This guide will help you get started.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use clear, descriptive titles** for new issues
3. **Provide detailed information**:
   - Environment details (OS, Python version, etc.)
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Error messages or logs
   - Relevant configuration

### Suggesting Features

1. **Check the roadmap** in README.md first
2. **Open a discussion** before implementing large features
3. **Describe the use case** and benefits
4. **Consider backward compatibility**

### Code Contributions

#### Setup Development Environment

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/ai-chatbot-vector-search.git
   cd ai-chatbot-vector-search
   ```

2. **Create development environment**
   ```bash
   cd training
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

#### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards below
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Test API connectivity
   python3 test-gemini-api.py
   
   # Test queue management
   python3 manage_queue.py status
   
   # Test training pipeline
   python3 training-job-gemini.py
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📋 Coding Standards

### Python Code Style

- **Follow PEP 8** style guidelines
- **Use meaningful variable names**
- **Add docstrings** to all functions and classes
- **Keep functions focused** and reasonably sized
- **Use type hints** where appropriate

### Example Function Documentation

```python
def process_content_directly(content: str, document_id: str, source: str, docs_count: int = 0) -> int:
    """
    Process content directly from queue message and return the number of documents processed.
    
    Args:
        content: The text content to process
        document_id: Unique identifier for the document
        source: Source system or identifier
        docs_count: Starting document count for ID generation
        
    Returns:
        Number of document chunks created and stored
        
    Raises:
        Exception: If content processing fails
    """
```

### Error Handling

- **Use specific exception types** when possible
- **Provide meaningful error messages**
- **Log errors appropriately**
- **Clean up resources** in finally blocks

```python
try:
    # risky operation
    result = process_data(data)
except SpecificException as e:
    logger.error(f"Failed to process data: {e}")
    raise
finally:
    # cleanup resources
    cleanup()
```

### Configuration Management

- **Use environment variables** for configuration
- **Provide sensible defaults**
- **Document all configuration options**
- **Validate configuration** at startup

### Testing Guidelines

- **Write tests for new features**
- **Test error conditions**
- **Use descriptive test names**
- **Mock external dependencies**

## 🏗️ Project Structure

```
ai-chatbot-vector-search/
├── README.md                 # Main project documentation
├── LICENSE                   # MIT License
├── CONTRIBUTING.md          # This file
├── .gitignore              # Git ignore rules
├── chatbot/                # Chatbot interface
│   ├── chat.py
│   ├── requirements.txt
│   └── Dockerfile
├── training/               # Training system
│   ├── training-job-gemini.py
│   ├── manage_queue.py
│   ├── test-gemini-api.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── README.md
│   └── Dockerfile
└── docs/                   # Additional documentation
    └── API.md
```

## 🚀 Areas for Contribution

### High Priority
- [ ] Unit and integration tests
- [ ] Performance optimization
- [ ] Better error handling and recovery
- [ ] Monitoring and metrics

### Medium Priority
- [ ] Web UI for queue management
- [ ] Batch processing support
- [ ] Multiple embedding model support
- [ ] Advanced search filters

### Low Priority
- [ ] REST API endpoints
- [ ] Kubernetes deployment configurations
- [ ] Monitoring dashboard
- [ ] Alternative vector databases

## 📝 Commit Message Convention

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat(training): add support for PDF document processing
fix(queue): handle SSL connection errors gracefully
docs(readme): update installation instructions
refactor(embeddings): improve error handling in embedding creation
```

## 🔍 Code Review Process

### For Contributors
- **Keep pull requests focused** and reasonably sized
- **Write clear PR descriptions** explaining the changes
- **Respond to feedback** promptly and professionally
- **Update your branch** if needed to resolve conflicts

### For Reviewers
- **Be constructive** and helpful in feedback
- **Focus on code quality** and project standards
- **Test the changes** when possible
- **Approve when ready** or request specific changes

## 🛡️ Security Guidelines

- **Never commit sensitive data** (API keys, passwords, etc.)
- **Use environment variables** for configuration
- **Validate all inputs** from external sources
- **Follow security best practices** for dependencies

## 📚 Documentation

### When to Update Documentation
- Adding new features
- Changing existing functionality
- Fixing bugs that affect usage
- Improving installation or setup process

### Documentation Types
- **README.md**: High-level project overview
- **training/README.md**: Detailed training system documentation
- **Code comments**: Inline documentation for complex logic
- **Docstrings**: Function and class documentation

## 🆘 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check README and training documentation first

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to make this project better! 🚀
