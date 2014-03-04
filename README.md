# JavaScript ESLint TextMate Bundle

Use the [ESLint](http://eslint.org/) JavaScript validator in [TextMate 2](https://github.com/textmate/textmate).

![Screenshot 1](https://raw.github.com/natesilva/eslint.tmbundle/master/no-errors.png)

## Features

* Validate automatically when you save your file, and on-demand.
* Shows you which `.eslintrc` settings are being used, with a direct link to open the applicable settings file.
* Errors and warnings include a link to the relevant explanation on [eslint.org](http://eslint.org/).

![Screenshot 2](https://raw.github.com/natesilva/eslint.tmbundle/master/with-errors.png)

## Install

First install ESLint:

1. Install [Node.js](http://nodejs.org/).
2. `[sudo] npm install -g eslint`

Now install the bundle:

1. [Download the latest release .zip file](https://github.com/natesilva/javascript-eslint.tmbundle/releases/latest).
2. Extract it.
3. Rename the extracted folder to `javascript-eslint.tmbundle`.
4. Double-click to install it in TextMate.

## Release Notes

Release notes are found in the [Releases](https://github.com/natesilva/javascript-eslint.tmbundle/releases) section of this GitHub repo.

## Configuration

In most cases no configuration is required. However, in some cases you may want to customize the following:

* **Use `eslint` that is not on your `PATH`:** If `eslint` is not on your `PATH`, set the `TM_JAVASCRIPT_ESLINT_ESLINT` variable to point to it. Set in *TextMate* > *Preferences…* > *Variables*.
* **Don’t validate on save:** If you don’t want to validate your JavaScript automatically when you press `⌘S`:
    1. Open the Bundle Editor (*Bundles* > *Edit Bundles…*).
    2. Navigate to *JavaScript ESLint* > *Menu Actions* > *Save & Validate with ESLint*.
    3. In the drawer that appears, delete the “Key Equivalent” of `⌘S`.
* **Use a project-specific ESLint configuration:**
    * `eslint` automatically uses `.eslintrc` files found in your directory tree. See the documentation on [configuring ESLint](http://eslint.org/docs/configuring/) for more information.
    
## Uninstall

1. Quit TextMate.
2. Open `~/Library/Application Support/Avian/Pristine Copy/Bundles`.
3. Trash `javascript-eslint.tmbundle`.
4. Open `~/Library/Application Support/Avian/Bundles`.
5. If there is a file called `JavaScript ESLint.tmbundle`, trash it.
6. You may need to clear TextMate’s cache by trashing `~/Library/Caches/com.macromates.TextMate.preview`.
