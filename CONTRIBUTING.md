# Contributor's Guide

To get started:

1. Clone the repo

   ```shell
   git clone https://github.com/demberto/DyCall
   ```

2. Browse to the newly created folder

   ```shell
   cd DyCall
   ```

3. Optionally setup a virtual environment:

   ```shell
   python -m venv .
   ```

4. Install dependencies:

   ```shell
   python -m pip install -r requirements-dev.txt -c constraints.txt
   python -m pip install -r requirements.txt -c constraints.txt
   ```

5. Install [tbump][tbump]. I don't include it in dependencies because it recommends
   using `pipx` for installation. You can choose the installation method you want. I
   used `pipx`.

## Coding Conventions

I have tried to follow an OO approach to DyCall. This might be best explained by the
answer to this question:

[Best way to structure a tkinter application?][so-17470842]

State variables are used wherever the content of a widget will be changed at runtime.
This implies that instead of

```python
entry = ttk.Entry()
entry.configure(text="Entry")
```

I use this approach

```python
entry_var = tk.StringVar()
entry = ttk.Entry(textvariable=entry_var)
entry_var.set("Entry")
```

This allows the top level window class `App` to create such state variables and pass
them to the sub-frames via their constructors. This allows for a sub frame to change the
contents of a widget inside another subframe without accessing the widget directly.

Additionally, events are generated where the use of control variable doesn't apply.
There are certain edge cases where events can't be used either due to Tkinter's
implementation of `Event` class not allowing arbitrary data to be retreived.

Apart from that, I have used LF line endings everywhere and tried to enforce it
everywhere I can - `.editorconfig` and `.gitattributes`

## Adding translations

DyCall uses `ttkbootstrap`'s `MessageCatalog` class to handle localizations. Existing
translations can be found in `dycall/msgs` folder. They are named with respect to their
[LCID][lcid] and need to be named that way. Tkinter (or Tk) doesn't need different files
for different locales but I have chosen to follow conventions.

You can add new strings to an existing translation or add a new one. To create a new
translation, follow these steps:

1. Create a new translation file in [dycall/msgs][dycall-msgs] named according to the
   LCID with a `.msg` extension

   > e.g. `hi.msg`.

2. To add a new string to in the file you just created follow this format:
   `::msgcat::mcset <LCID> "<String in English>" "<Translated string>"`

   > e.g.
   >
   > ```tk
   > ::msgcat::mcset hi "Hindi" "हिंदी"
   > ```
   >
   > _Don't miss the quotation marks_

3. In [dycall/util.py][dycall-util-py], add a key-value pair to the `LCID2Lang`
   dictionary in the format of `<LCID>: <Language name in its native form>`

   > e.g.
   >
   > ```python
   > "hi": "हिंदी"
   > ```

   The value will be used as an option under **Options** ➔ **Language** submenu in the
   DyCall interace.

The process for updating existing translations is pretty much the same. Just begin from
step 2 directly

> **If the translations don't work**
>
> You need to ensure `MessageCatalog.translate` is getting called like this:
>
> ```python
> from ttkbootstrap.localization import MessageCatalog as MC
>
> # Somewhere in the code
> translated = MC.translate("Translate me!")
> ```

## Appearance

I tried many themes for and solutions for implementing dark/light themses. Almost all of
these solutions work with images and are extremely laggy, so I chose TtkBootstrap.

TtkBootstrap has tons of almost same looking themes. Of them, the `darkly` theme looks
most native on Windows and blends perfectly with `tksheet`'s `dark blue` theme. I don't
actually like any oh the light mode themes TTkBootstrap has, all of them are too bright
and look nothing close to native, but `yeti` still feels a bit better.

I think 2 themes are enough, DyCall is a utility tool after all.

<!-- MARKDOWN LINKS -->

[dycall-msgs]: https://github.com/demberto/DyCall/tree/master/dycall/msgs
[dycall-util-py]: https://github.com/demberto/DyCall/blob/master/dycall/util.py
[lcid]: https://www.tcl.tk/man/tcl8.7/TclCmd/msgcat.html#M23
[so-17470842]: https://stackoverflow.com/a/17470842
[tbump]: https://github.com/dmerejkowsky/tbump
