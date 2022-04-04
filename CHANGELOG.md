# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.6] - 2022-04-04

**All the images got corrupted in v0.0.5. This makes the previous version as
well as 0.0.4 unusable.** I should have tested better. How these images got
corrupted is beyond me. In case it ever happens again, I am including a
command-line option to run DyCall without loading any images.

*Interestingly enough, the changes I made to repair the corrupted images
disappeared when I staged them.*

### Added

- Command line option `--no-images`.

### Fixed

- All corrupted images.
- Added padding to the license text in the **About** window.
- `--hide-errno` was mistakenly made a Windows only option instead of
  `--hide-gle`.

### Removed

- Redundant check in publish CI action.

## [0.0.5] - 2022-03-29

### Added

- Update check button in **About**.
- Installed version of DyCall and its dependencies is displayed in **About**.
- `publish` action automatically creates a release with changelogs from here.
- Auto add/remove rows in **Exports** treeview when resized.
- The code is now vastly more documented, almost no class or function is left.

### Changed

- **About** window will not get created if its open already (singleton).
- App icon setter logic, handled for all windows in `App` itself.
- `util.py`: `get_png` renamed to `get_img`.

### Removed

- `util.py`: `set_app_icon` method.

## [0.0.4] - 2022-03-24

### Added

- Support for recent files via **File** > **Open Recent**.
- GitHub project repo link to **About** page.
- Script to pad square images.
- Icons to certain top menu options.
- `F1` accelerator to open **About** page.
- Emojis to README.
- Script to recolor icons.
- Exports treeview to get detailed information.
- Ability to sort exports (ascending/descending).
- `errno` and `GetLastError` (Windows only) error codes in status bar.

### Changed

- **Exports** combobox is now editable.
- **Demangler**'s _Demangle_ button works only when text is present.
- Events and control variables are used for inter-sub-widget communication
  instead of directly accessing them through `parent` instance.

### Fixed

- CI actions.
- Entry point name.
- **Picker** entry validation logic.
- Many fixes for Linux.

## [0.0.3] - 2022-03-10

Initial release.

[0.0.6]: https://github.com/demberto/DyCall/compare/v0.0.5...v0.0.6
[0.0.5]: https://github.com/demberto/DyCall/compare/v0.0.4...v0.0.5
[0.0.4]: https://github.com/demberto/DyCall/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/demberto/DyCall/releases/tag/v0.0.3
