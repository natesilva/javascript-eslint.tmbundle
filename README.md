# JavaScript ESLint TextMate Bundle

Use the [ESLint](http://eslint.org/) JavaScript validator in [TextMate 2](https://github.com/textmate/textmate).

(Want to use JSHint instead? Try the [jshint-external.tmbundle](https://github.com/natesilva/jshint-external.tmbundle))

<img src="http://natesilva.github.io/javascript-eslint.tmbundle/images/no-errors-2.0.0.png" width="500" style="width:560px;" alt="Screenshot 1">

## Features

* Validate automatically when you save your file, and on-demand.
* Supports ESLint’s native configuration cascading.
* Errors and warnings include a link to the relevant explanation on [eslint.org](http://eslint.org/).

<img src="http://natesilva.github.io/javascript-eslint.tmbundle/images/with-errors-2.0.0.png" width="500" style="width:560px;" alt="Screenshot 2">

## Install

First install ESLint:

1. Install [Node.js](http://nodejs.org/).
2. `[sudo] npm install -g eslint`
3. (Optional) Create a starter ESLint configuration: `eslint --init`

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
2. Open `~/Library/Application Support/Avian/Pristine Copy/Bundles`.
3. Trash `javascript-eslint.tmbundle`.
4. Open `~/Library/Application Support/Avian/Bundles`.
5. If there is a file called `JavaScript ESLint.tmbundle`, trash it.
6. You may need to clear TextMate’s cache by trashing `~/Library/Caches/com.macromates.TextMate.preview`.
