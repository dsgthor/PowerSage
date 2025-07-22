name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    name: Test on Python ${{ matrix.python-version }}
    runs-on: windows-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install psutil pystray pillow plyer keyboard
        pip install pyinstaller

    - name: Lint with flake8 (if available)
      run: |
        pip install flake8
        # Stop the build if there are Python syntax errors or undefined names
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        # Exit-zero treats all errors as warnings
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
      continue-on-error: true

    - name: Test script syntax
      run: |
        python -m py_compile powerwhisper_complete5.py

    - name: Test imports and basic functionality
      run: |
        python -c "
        import sys
        sys.argv = ['test']  # Prevent GUI from starting
        try:
            import powerwhisper_complete5
            print('✅ Import successful')
        except Exception as e:
            print(f'❌ Import failed: {e}')
            sys.exit(1)
        "

  build:
    name: Build Executable
    needs: test
    runs-on: windows-latest
    if: startsWith(github.ref, 'refs/tags/v')

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install psutil pystray pillow plyer keyboard pyinstaller

    - name: Build executable
      run: |
        pyinstaller --noconfirm --onefile --windowed --name PowerWhisper powerwhisper_complete5.py

    - name: Test executable exists
      run: |
        if (Test-Path "dist/PowerWhisper.exe") {
          echo "✅ Executable built successfully"
          Get-Item "dist/PowerWhisper.exe" | Select-Object Name, Length, LastWriteTime
        } else {
          echo "❌ Executable not found"
          exit 1
        }

    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: PowerWhisper-${{ github.ref_name }}-windows-x64
        path: dist/PowerWhisper.exe
        retention-days: 30

  release:
    name: Create Release
    needs: [test, build]
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Download artifact
      uses: actions/download-artifact@v3
      with:
        name: PowerWhisper-${{ github.ref_name }}-windows-x64
        path: ./release

    - name: Generate release notes
      id: release_notes
      run: |
        # Extract version from tag
        VERSION=${GITHUB_REF#refs/tags/}
        echo "VERSION=$VERSION" >> $GITHUB_OUTPUT
        
        # Generate release notes from CHANGELOG.md if available
        if [ -f "CHANGELOG.md" ]; then
          # Extract notes for this version (basic implementation)
          echo "RELEASE_NOTES<<EOF" >> $GITHUB_OUTPUT
          echo "## PowerWhisper $VERSION" >> $GITHUB_OUTPUT
          echo "" >> $GITHUB_OUTPUT
          echo "### 🚀 What's New" >> $GITHUB_OUTPUT
          echo "- See [CHANGELOG.md](CHANGELOG.md) for detailed changes" >> $GITHUB_OUTPUT
          echo "" >> $GITHUB_OUTPUT
          echo "### 📦 Downloads" >> $GITHUB_OUTPUT
          echo "- **Windows Executable**: PowerWhisper.exe (standalone, no Python required)" >> $GITHUB_OUTPUT
          echo "- **Source Code**: Available as zip/tar.gz" >> $GITHUB_OUTPUT
          echo "" >> $GITHUB_OUTPUT
          echo "### 💻 System Requirements" >> $GITHUB_OUTPUT
          echo "- Windows 10 or 11" >> $GITHUB_OUTPUT
          echo "- x64 architecture" >> $GITHUB_OUTPUT
          echo "- Administrator privileges (recommended)" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
        else
          echo "RELEASE_NOTES=PowerWhisper $VERSION release" >> $GITHUB_OUTPUT
        fi

    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref_name }}
        release_name: PowerWhisper ${{ steps.release_notes.outputs.VERSION }}
        body: ${{ steps.release_notes.outputs.RELEASE_NOTES }}
        draft: false
        prerelease: false

    - name: Upload Release Asset
      uses: actions/upload-release-asset@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        upload_url: ${{ steps.create_release.outputs.upload_url }}
        asset_path: ./release/PowerWhisper.exe
        asset_name: PowerWhisper-${{ steps.release_notes.outputs.VERSION }}-windows-x64.exe
        asset_content_type: application/octet-stream

  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    if: github.event_name == 'push' || github.event_name == 'pull_request'

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'