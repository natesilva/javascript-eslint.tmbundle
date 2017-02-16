# JavaScript ESLint TextMate Bundle

Use the [ESLint](http://eslint.org/) JavaScript validator in [TextMate 2](https://github.com/textmate/textmate).

<video autoplay="autoplay" loop="loop" width="366" height="114">
  <source src="https://natesilva.github.io/javascript-eslint.tmbundle/images/gutter-popup.mp4" type="video/mp4" />
  <img src="https://natesilva.github.io/javascript-eslint.tmbundle/images/gutter-popup.gif" width="366" height="114" alt="ESLint errors and warnings in the TextMate gutter"></video>

## Features

* Validate automatically when you save your file, and on-demand.
* Auto-fix errors using the ESLint `--fix` command.
* Errors and warnings are displayed in the TextMate gutter.
* Optionally get a report listing errors and warnings with links to the relevant explanations on [eslint.org](http://eslint.org/).
* Supports ESLint’s native configuration cascading.

<img src="https://natesilva.github.io/javascript-eslint.tmbundle/images/fix-menu.png" width="300" style="width:300px;" alt="Use ESLint to auto-fix errors and warnings">

<img src="https://natesilva.github.io/javascript-eslint.tmbundle/images/validation-report.png" width="550" style="width:550px;" alt="Optional validation report">

## Install

First install ESLint:

* In your project
  * `npm install --save eslint`
* Or globally
  * `[sudo] npm install -g eslint`

(Optional) Create a starter ESLint configuration: `eslint --init`

Now install the bundle:

1. [Download the latest release .zip file](https://github.com/natesilva/javascript-eslint.tmbundle/releases/latest).
2. Extract it and double-click to install in TextMate.

## Release Notes

<a href="https://github.com/natesilva/javascript-eslint.tmbundle/releases">View the release notes.</a>

## Configuration

In most cases no configuration is required. However, in some cases you may want to customize the following:

* **Use `eslint` that is not on your `PATH`:** If `eslint` is not on your `PATH`, set the `TM_JAVASCRIPT_ESLINT_ESLINT` variable to point to it. Set in *TextMate* > *Preferences…* > *Variables*.
* **Don’t validate on save:** If you don’t want to validate your JavaScript automatically when you press `⌘S`:
    1. Open the Bundle Editor (*Bundles* > *Edit Bundles…*).
    2. Navigate to *JavaScript ESLint* > *Menu Actions* > *Save & Validate with ESLint*.
    3. In the drawer that appears, delete the “Key Equivalent” of `⌘S`.
* **Use a project-specific ESLint configuration:**
    * `eslint` automatically uses `.eslintrc` and `package.json` files found in your directory tree. See [the documentation](http://eslint.org/docs/user-guide/configuring#configuration-cascading-and-hierarchy) for more information.

## Uninstall

1. Quit TextMate.
2. Open `~/Library/Application Support/TextMate/Pristine Copy/Bundles`.
3. Trash `javascript-eslint.tmbundle`.
4. Open `~/Library/Application Support/Avian/Bundles`.
5. If there is a file called `JavaScript ESLint.tmbundle`, trash it.
6. You may need to clear TextMate’s cache by trashing `~/Library/Caches/com.macromates.TextMate`.
