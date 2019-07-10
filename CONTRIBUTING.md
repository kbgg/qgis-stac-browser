# Contribution Guidelines

Before opening any issues or proposing any pull requests, please read
this document in its entirety.

## Questions

The GitHub issue tracker is for *bug reports* and *feature requests*. Please do
not use it to ask questions about how to use this plugin. For questions about
usage refer to the documentation. If your question is not answered in the
documentation, join the [gitter](https://gitter.im/qgis-stac-browser/community)
and ask your questions there.

## Good Bug Reports

Please be aware of the following things when filing bug reports:

1. Avoid raising duplicate issues. *Please* use the GitHub issue search feature
   to check whether your bug report or feature request has been mentioned in
   the past. Duplicate bug reports and feature requests are a huge maintenance
   burden on the limited resources of the project. If it is clear from your
   report that you would have struggled to find the original, that's ok, but
   if searching for a selection of words in your issue title would have found
   the duplicate then the issue will likely be closed extremely abruptly.
2. When filing bug reports about exceptions or tracebacks, please include the
   *complete* traceback. Partial tracebacks, or just the exception text, are
   not helpful.
3. Make sure you provide a suitable amount of information to work with. This
   means you should provide:

   - Guidance on **how to reproduce the issue**. Ideally, this should be a
     list of steps that can be taken to reproduce the issue.
     Failing that, let us know what you're doing, how often it happens, what
     environment you're using, etc. Be thorough: it prevents us needing to ask
     further questions.
   - Tell us **what you expected to happen**. When we follow your steps,
     what are we expecting to happen? What does "success" look like for your
     process?
   - Tell us **what actually happens**. It's not helpful for you to say "it
     doesn't work" or "it fails". Tell us *how* it fails: do you get an
     exception? A hang? A non-200 status code? How was the actual result
     different from your expected result?
   - Tell us **what version of QGIS STAC Browser you're using**, and
     **how you installed it**. Different versions of QGIS STAC Browser behave
     differently and have different bugs.

   If you do not provide all of these things, it will take us much longer to
   fix your problem. If we ask you to clarify these and you never respond, we
   will close your issue without fixing it.
   
## Pull Requests

Good pull requests should follow these guidelines:

1. Make your pull request merge into the `dev` branch. The `master` branch
   is reserved for the current stable release while the `dev` branch is the 
   working branch.
   
2. Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008) style guide.
   There are a few exceptions to this style guide which are allowed:
   
   - Lines should be a maximum of 79 characters long.
   - Lines can be 99 characters long when inconvieniet.
   - Lines can be a maximum of 119 characters long in extreme cases.
   - Qt widget names should be in camel case to follow Qt convention.
   - Qt widget names should end in the type of widget (i.e. cancelButton, dateLabel).
   - Classes which interact with QGIS/Qt should use camelCase for their property, method and variable names.
   - Event callbacks should be marked private.
   
3. Implement type hints for all functions/methods ([PEP 484](https://www.python.org/dev/peps/pep-0484/))

4. Make sure your code passes all linting and test requirements before submitting your pull request.

