name: 🐛 Bug Report
description: Report a bug or issue with PowerWhisper
title: "[Bug]: "
labels: ["bug", "needs-triage"]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to report a bug! Please fill out the information below to help us diagnose the issue.

  - type: textarea
    id: description
    attributes:
      label: Bug Description
      description: A clear and concise description of what the bug is.
      placeholder: Describe the bug...
    validations:
      required: true

  - type: textarea
    id: reproduce
    attributes:
      label: Steps to Reproduce
      description: Steps to reproduce the behavior
      placeholder: |
        1. Go to '...'
        2. Click on '....'
        3. Scroll down to '....'
        4. See error
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: A clear and concise description of what you expected to happen.
      placeholder: What should have happened?
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: Actual Behavior
      description: What actually happened instead?
      placeholder: What actually happened?
    validations:
      required: true

  - type: dropdown
    id: windows-version
    attributes:
      label: Windows Version
      description: What version of Windows are you running?
      options:
        - Windows 11
        - Windows 10
        - Other (please specify in additional context)
    validations:
      required: true

  - type: input
    id: python-version
    attributes:
      label: Python Version
      description: What version of Python are you using?
      placeholder: e.g., 3.12.0
    validations:
      required: true

  - type: dropdown
    id: admin-rights
    attributes:
      label: Administrator Rights
      description: Are you running PowerWhisper with administrator privileges?
      options:
        - "Yes"
        - "No"
        - "Not sure"
    validations:
      required: true

  - type: dropdown
    id: installation-method
    attributes:
      label: Installation Method
      description: How did you install/run PowerWhisper?
      options:
        - "Python script directly"
        - "Compiled .exe"
        - "Other"
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Log Output
      description: |
        Please include relevant excerpts from `powerwhisper.log`. 
        **DO NOT paste your entire log file** - just the relevant error messages or the last 20-30 lines.
      placeholder: Paste relevant log excerpts here...
      render: shell

  - type: textarea
    id: screenshots
    attributes:
      label: Screenshots
      description: If applicable, add screenshots to help explain your problem.
      placeholder: You can paste images directly here

  - type: textarea
    id: additional-context
    attributes:
      label: Additional Context
      description: Add any other context about the problem here (hardware, other running software, etc.)
      placeholder: Any additional information that might be helpful...

  - type: checkboxes
    id: checklist
    attributes:
      label: Pre-submission Checklist
      description: Please check the following before submitting
      options:
        - label: I have searched existing issues to make sure this isn't a duplicate
          required: true
        - label: I have checked the troubleshooting section in the README
          required: true
        - label: I have included relevant log excerpts (not the entire log file)
          required: false