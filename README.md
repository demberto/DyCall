<!-- PROJECT SHIELDS -->

![Integrity Action Status][integrity-status]
![Publish Action Status][publish-status]
[![MIT License][license-shield]][license-url]
[![Python Versions][pyversions-shield]][pyversions-url]
[![Package Version][package-version-shield]][package-version-url]
[![security: bandit][bandit-shield]][bandit-url]
[![Code Style: Black][code-style-shield]][code-style-url]

<div align="center">
  <img width="128" height="128" src="https://raw.githubusercontent.com/demberto/DyCall/master/ext/dycall.png">
  <h2>DyCall</h2>
  <h3>Run exported symbols from native libraries</h3>
</div>

## ℹ About

DyCall is a cross platform GUI application which lets you call exported functions from
platform-native libraries.

_"libraries" refers to dynamic libraries (a.k.a shared objects etc.)._

### ⚡ Features

- 🔎 Follows platform-specific library search order.
- 🧹 Automatic export name demangling for native libraries.
- #️⃣ Support for ordinal-only exports.
- ↪️ Support for _out_ variables.
- 💡 Find out export names for non-native libraries as well.
- 🛠 Standalone demangler for native ABI mangled names.
- 🔆 Light and dark themes.
- 📜 Multi-lingual interface. Currently only Hindi and Marathi are supported.

## 🚲 Getting Started

DyCall requires Python 3.7+ with Tkinter installed.

Install via `pip`:

```none
python -m pip install dycall
```

You can run it via:

```none
python -m dycall-gui
```

You can also install shortcuts (Windows and Linux only):

```none
python -m desktop-app install dycall
```

This will create shortcuts in Windows start menu or an equivalent place on Linux. You
can then run DyCall like any other app, pin it, etc.

To uninstall, first remove any shortcuts if you installed them:

```none
python -m desktop-app uninstall dycall
```

Then uninstall DyCall via pip:

```none
python -m pip uninstall dycall
```

## ▶ Usage

_The interface has changed a bit since I recorded this GIF_

<div align="center">
  <img src="https://raw.githubusercontent.com/demberto/DyCall/master/ext/usage.gif"/>
</div>

## ❔ FAQ

### 1️⃣ Is it non-blocking?

Yes! Function calls are executed on a separate thread. Although, you cannot close DyCall
while a function is running. I don't think that's possible.

### 2️⃣ How do I pass `nullptr` or `NULL` as an argument?

Select **Type** as `void`

### 3️⃣ How do I pass Win32 data types?

Win32 data types are just `typedef`s to basic C data types.

Use this table below for finding out the correct type to use:

| Win32          | DyCall    |
| -------------- | --------- |
| PCSTR, LPCSTR  | char\*    |
| PWSTR, LPCWSTR | wchar_t\* |
| BYTE           | uint8_t   |
| WORD           | uint16_t  |
| DWORD          | uint32_t  |
| HANDLE         | void\*    |

### 4️⃣ How to pass _out_ variables?

There are no special data types for _out_ parameters, just pass them as normal types,
the changed values will be reflected after execution finishes.

### 5️⃣ How to pass a buffer for an _out_ string?

When using **OUT Mode** for strings, please ensure that none of the arguments are
overwritten to a value whose size/length is greater than that before calling; i.e. input
argument size **must be** equal to or greater than output argument size. If this is not
the case, you can fill the _out_ argument value with random data of length you **know
for sure** is greater than what the _out_ string will have. Since DyCall has no
mechanism to preallocate string buffers, attempts to read beyond the `NULL` character
will result in memory violation errors and crash DyCall.

### 6️⃣ How to find an ordinal-only export?

Ordinal-only exports have names starting with an `@` followed by the ordinal number.

### 7️⃣ I want to add/update a translation

Check the [Adding Translations][adding-translations] section in the contributor's guide.

## 🚀 Roadmap

- [ ] Automatic call convention detection.
- [ ] Function prototype detection from header files or similar.
- [ ] Use a child process to execute, this ensures more stability.

## 🤝 Contributing

Please check the contributor's [guide][contributor-guide].

You can contribute by adding translations, opening issues and filing pull requests. If
that cannot be an option for you, you can directly drop an [email](#contact). All
contributions are welcome and acknowledged.

Contributors should also take a note of the [Code of Conduct][code-of-conduct].

## © License

**DyCall** is distributed under the MIT License. See `LICENSE` for more information.

## 📧 Contact

E-mail: demberto@protonmail.com

## 🙏 Acknowledgments

- [FlatIcon](https://flaticon.com)
- [Best-README-Template](https://github.com/othneildrew/Best-README-Template)
- [Shields](https://shields.io)
- [Keep A Changelog](https://keepachangelog.com)

Additional acknowledgements have been made in the code.

<!-- MARKDOWN LINKS AND IMAGES -->

[adding-translations]: https://github.com/demberto/DyCall/blob/master/CONTRIBUTING.md#adding-translations
[bandit-shield]: https://img.shields.io/badge/security-bandit-yellow.svg
[bandit-url]: https://github.com/PyCQA/bandit
[code-style-shield]: https://img.shields.io/badge/code%20style-black-black
[code-style-url]: https://github.com/psf/black
[code-of-conduct]: https://github.com/demberto/DyCall/blob/master/CODE_OF_CONDUCT.md
[contributor-guide]: https://github.com/demberto/DyCall/blob/master/CONTRIBUTING.md
[integrity-status]: https://img.shields.io/github/workflow/status/demberto/DyCall/integrity?label=integrity
[license-shield]: https://img.shields.io/pypi/l/dycall
[license-url]: https://github.com/demberto/DyCall/blob/master/LICENSE
[publish-status]: https://img.shields.io/github/workflow/status/demberto/DyCall/publish?label=publish
[pyversions-shield]: https://img.shields.io/pypi/pyversions/dycall
[pyversions-url]: https://pypi.org/project/dycall
[package-version-shield]: https://img.shields.io/pypi/v/dycall
[package-version-url]: https://pypi.org/project/dycall
