# IssueTracker V0.3 Monday, April 18, 2016 Ariana Giroux, Eclectick Media Solutions

## Updating and maintenance of this directory.

You can submit new files using IssueTracker V0.3 available at:

    github.org/eclectickeclipse/issuetracker

To maaintain or update the files in this directory, use:

    IssueTracker -s <PATH/TO/CODEFILE> -p <PATH/TO/DIR/> <BUGTAG>

## BUG TAGS in your code.

In languages that allow for commenting with the # character, you can make a new BUG TAG by including a comment as
follows

    # TODO BUG <BUGNAME>: comment text.

The program will save any text on the right of the colon, the line number, and the filename to a file.

The syntax is chosen to enable readability and brevity of the tag.

As of V0.3, this program does not support custom search patterns for use in languages that do not allow "# TODO"
comments.
