# Xliff Pseudo Translator

An application for creating "pseudo translations" based on English text. These "translations" read like English, but use accented characters to highlight that the string is a translation. This is helpful for testing websites and ensuring that all of the strings are being marked for a translation.

This application is designed to be used with Angular's i18n extraction, although it will work on any xliff 1.2 file. The benefit over other pseudo translation tools is that this tool respects ICU expressions. To use an example from the Angular documentation, consider the string `Updated {minutes, plural, =0 {just now} =1 {one minute ago} other {{{minutes}} minutes ago}}`. In this example, `{minutes, plural, ...` and `other {{{minutes}}` should all not be translated, as they represent variable names.
