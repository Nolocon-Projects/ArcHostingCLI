# ArcHosting Command Line Interface

ArcHosting CLI is a simple tool that uses Git to synchronize a server between different devices and allows other players to join through tunneling.

## Requirements

* Python (if using the source code instead of a release) (Python 3.14.5 recommended)
* Git
* A GitHub account for cloud services

## Installation

### Running from Source

You can run the code yourself. Make sure all requirements are installed.

#### Downloading the Code

##### [A] Using Git

If Git is installed, navigate to any directory and run:

```bash
git clone https://github.com/Nolocon-Projects/ArcHostingCLI
```

##### [B] Using GitHub CLI

If you prefer GitHub CLI, navigate to any directory and run:

```bash
gh repo clone Nolocon-Projects/ArcHostingCLI
```

##### [C] Downloading a ZIP Archive

You can also click the green **Code** button on the GitHub page and download the ZIP archive. Make sure to extract it to your desired location.

#### Adding ArcCLI to Your PATH

To use ArcCLI globally, add its directory to your system's PATH environment variable. This allows the `arc` command to be recognized from anywhere.

#### Executing the Code

You can now run:

```bash
python main.py [ARGUMENTS]
```

to use ArcHosting CLI.

Make sure Python has been added to your PATH. Otherwise, replace `python` with the full path to your Python executable.

You can also create an alias to use shorter commands such as:

```bash
arc server
```

Refer to your operating system's documentation for instructions on creating aliases.

### Using the Portable Release

You can use a portable release of ArcCLI. Please note that some additional setup may be required.

#### Downloading the Release

Go to the repository's Releases page. Select the version you want and download either the portable `.exe` (Windows) or Linux binary. Copy it to your preferred location.

#### [Optional but Recommended] Adding the Portable Version to PATH

To use the CLI globally, add the directory containing the executable to your PATH environment variable. Otherwise, the executable will only work when run from its own directory.

Refer to your operating system's documentation for instructions on modifying the PATH variable.

#### Using the Portable Version

If ArcCLI has been added to your PATH, you can use it with the `arc` command. Otherwise, run it using its full file path.

### Using the Installer

ArcCLI includes installers for both Windows and Linux.

Go to the Releases page, download the installer for your operating system, and run it.

**Note:** On most Linux distributions, you must first make the installer executable:

```bash
chmod +x [FILENAME]
```

Then follow the installer's instructions. Once installation is complete, ArcCLI will be available system-wide.
