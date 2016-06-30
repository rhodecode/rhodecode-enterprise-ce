
==================================================
 Code style and structure guide for frontend work
==================================================

About: Outline of frontend development practices.




Templates
=========

- Indent with 4 spaces in general.

- Embedded Python code follows the same conventions as in the backend.

  A common problem are missed spaces around operators.




Grunt AND npm2nix
=================


---something goes here ---




LESS CSS
========


Style
-----

- Use 4 spaces instead of tabs.

- Avoid ``!important``, it is very often an indicator for a problem.




Structure
---------

It is important that we maintain consistency in the LESS files so that things
scale properly. CSS is organized using LESS and then compiled into a css file
to be used in production. Find the class you need to change and change it
there. Do not add overriding styles at the end of the file. The LESS file will
be minified; use plenty of spacing and comments for readability.

These will be kept in auxillary LESS files to be imported (in this order) at the top:

- `fonts.less` (font-face declarations)
- `mixins` (place all LESS mixins here)
- `helpers` (basic classes for hiding mobile elements, centering, etc)
- `variables` (theme-specific colors, spacing, and fonts which might change later)


Sections of the primary LESS file are as follows. Add comments describing
layout and modules.

.. code-block:: css

   //--- BASE ------------------//
           Very basic, sitewide styles.

   //--- LAYOUT ------------------//
           Essential layout, ex. containers and wrappers.
           Do not put type styles in here.

   //--- MODULES ------------------//
           Reusable sections, such as sidebars and menus.

   //--- THEME ------------------//
           Theme styles, typography, etc.



Formatting rules
~~~~~~~~~~~~~~~~

- Each rule should be indented on a separate line (this is helpful for diff
  checking).

- Use a space after each colon and a semicolon after each last rule.

- Put a blank line between each class.

- Nested classes should be listed after the parent class' rules, separated with a
  blank line, and indented.

- Using the below as a guide, place each rule in order of its effect on content,
  layout, sizing, and last listing minor style changes such as font color and
  backgrounds. Not every possible rule is listed here; when adding new ones,
  judge where it should go in the list based on that hierarchy.

  .. code-block:: scss

     .class {
             content
             list-style-type
             position
             float
             top
             right
             bottom
             left
             height
             max-height
             min-height
             width
             max-width
             min-width
             margin
             padding
             indent
             vertical-align
             text-align
             border
             border-radius
             font-size
             line-height
             font
             font-style
             font-variant
             font-weight
             color
             text-shadow
             background
             background-color
             box-shadow
             background-url
             background-position
             background-repeat
             background-cover
             transitions
             cursor
             pointer-events

             .nested-class {
                     position
                     background-color

                     &:hover {
                             color
                     }
             }
     }
