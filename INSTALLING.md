This page accumulates known technical information on installing, developing, and testing the test-report service.

## Table of contents

* [Local development and debugging](#local-development-and-debugging)
* [Test runtime](#tests)


<a name="local-development-and-debugging"></a>
## Local development and debugging

```bash
# Get Makefile help
make

# Install dependencies
make install

# Start the development server
make test-webserver

# Check linting python code
make linting

# Format your code automatically
make fmt
```

<a name="tests"></a>
## **Test runtime**

```bash
# Run unit-tests
make test

```