# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2024-12-23
### Added
- User Interface:
  - Status bar with:
    - Last save timestamp
    - Word and character count
    - Current theme
    - File path display

- Customizable Theme:
  - Themes can be changed from command palette
  - Syntax highlighting themes
  - High contrast theme for accessibility

### Fixed
- Command palette now correctly displays and updates the current theme

## [0.1.0] - 2024-12-22
### Added
- Core Editor Features:
  - Full-featured markdown text editor
  - Real-time syntax highlighting
  - Soft wrap text support
  - Table of Contents generation with proper linking
  - Command palette for quick actions

- Preview System:
  - Live markdown preview panel
  - Split-screen view with adjustable width
  - Toggle preview visibility
  - Synchronized scrolling

- File Management:
  - Automatic file saving
  - Backup system with timestamps
  - File state logging
  - New file creation support
  - File modification detection

- Command System:
  - Command palette interface
  - Keyboard shortcuts:
    - Save (Ctrl+S)
    - Toggle Preview (Ctrl+@)
    - Adjust Panel Width (Ctrl+L/Q)
    - Generate TOC (Ctrl+B)

- Export:
  - Export to PDF
  - Export to HTML
  - Export to DOCX
  - Custom export templates
