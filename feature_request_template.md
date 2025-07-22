name: ✨ Feature Request
description: Suggest a new feature or enhancement for PowerWhisper
title: "[Feature]: "
labels: ["enhancement", "needs-triage"]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        Thank you for suggesting a new feature! Please provide as much detail as possible.

  - type: textarea
    id: feature-description
    attributes:
      label: Feature Description
      description: A clear and concise description of the feature you'd like to see.
      placeholder: Describe the feature...
    validations:
      required: true

  - type: textarea
    id: problem-solving
    attributes:
      label: Problem This Solves
      description: What problem would this feature solve? What pain point does it address?
      placeholder: This would help with...
    validations:
      required: true

  - type: textarea
    id: use-case
    attributes:
      label: Use Case
      description: Describe when and how you would use this feature.
      placeholder: I would use this when...
    validations:
      required: true

  - type: textarea
    id: proposed-solution
    attributes:
      label: Proposed Solution
      description: How do you envision this feature working? Be as specific as possible.
      placeholder: This could work by...
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: Alternative Solutions
      description: Have you considered any alternative solutions or workarounds?
      placeholder: I've also considered...

  - type: dropdown
    id: priority
    attributes:
      label: Priority Level
      description: How important is this feature to you?
      options:
        - "Nice to have"
        - "Would be helpful"
        - "Important for my use case"
        - "Critical/blocking"
    validations:
      required: true

  - type: dropdown
    id: complexity
    attributes:
      label: Implementation Complexity (Your Estimate)
      description: How complex do you think this feature would be to implement?
      options:
        - "Simple (minor change)"
        - "Moderate (new functionality)"
        - "Complex (significant changes)"
        - "Not sure"

  - type: textarea
    id: mockups
    attributes:
      label: Mockups or Examples
      description: |
        If applicable, add mockups, sketches, or examples from other applications.
        You can paste images directly here.
      placeholder: You can paste images or describe UI changes here...

  - type: textarea
    id: additional-context
    attributes:
      label: Additional Context
      description: Any other context, links, or information about the feature request.
      placeholder: Additional details...

  - type: checkboxes
    id: checklist
    attributes:
      label: Pre-submission Checklist
      description: Please check the following before submitting
      options:
        - label: I have checked the roadmap in README.md to see if this is already planned
          required: true
        - label: I have searched existing issues to make sure this isn't a duplicate
          required: true
        - label: This feature would be beneficial to other users, not just my specific case
          required: true