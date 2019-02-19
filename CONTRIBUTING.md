# Introduction

Thank you for considering contributing to the ANTS project.

This set of instructions and rules is based on a template found [here](https://github.com/nayafia/contributing-template).

Following these guidelines helps establish consistency, reliability, and (most importantly) efficiency in the development of the project. We are currently a small group of students and post-doctorates, and the benefits of structure across all levels of the current and future project plans is immeasurable.

Contributions of any kind, whether they are in the form of documentation, new features, enhancements to existing features, recommendations, or bug fixes are always welcome. However, it is important that any additions and/or changes made to the ANTS project follow the Golden Rule, in a way; while we currently don't have a complete style standard or any gating requirements for a commit, it is essential that contributions observe the following tenets:

1. Write clear, concise code that is broken up into logical blocks. **Don't** contribute code that others would need to clean up themselves to be able to use or understand.
2. Communicate the process you've gone through in contributing - e.g. explain the steps in the development of your feature or investigation of a bug. **Don't** make a surprise change and send a pull request. **Any changes you make should be reviewed by at least one other contributor before it can be incorporated.**
3. Test your code to the best of your ability, and document those tests. If it's a minimal change, make sure it's documented and note what the results were when you tested it.

# Ground Rules

## Responsibilities
* Create issues for any major changes and enhancements that you wish to make. Discuss things transparently and get community feedback.
* Don't add any classes to the codebase without discussing their purpose with other team members. Err on the side of using functions.
* Keep feature versions as small as possible, preferably one new feature per version.
* Be helpful to new or otherwise less familiar team members - you will need their help sooner rather than later.

# Your First Contribution

Unsure where to begin contributing to ANTS? You can start by looking through these beginner and help-wanted issues:
* Beginner issues - issues which should only require a few lines of code, and a test or two.
* Help wanted issues - issues which should be a bit more involved than beginner issues.

Here are a couple of friendly tutorials: http://makeapullrequest.com/ and http://www.firsttimersonly.com/

* Working on your first Pull Request? You can learn how from this *free* series, [How to Contribute to an Open Source Project on GitHub](https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github).

At this point, you're ready to make your changes! Feel free to ask for help; everyone is a beginner at first :smile_cat:

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your branch so it's easier to merge.

# Getting started

For something that is bigger than a one or two line fix:

1. Create your own fork of the code
2. Do the changes in your fork
3. If you like the change and think the project could use it:
    * Be sure you have followed the code style for the project (control.py is currently the gold standard for style).
    * Send a pull request with a detailed description to at least two other contributors from the master repo.

Small contributions such as fixing spelling errors, where the content is small enough to not be considered intellectual property, can be submitted by a contributor as a patch.

As a rule of thumb, changes are obvious fixes if they do not introduce any new functionality or creative thinking. As long as the change does not affect functionality, some likely examples include the following:
* Spelling / grammar fixes
* Typo correction, white space and formatting changes
* Comment clean up
* Bug fixes that change default return values or error codes stored in constants
* Adding logging messages or debugging output
* Changes to ‘metadata’ files like .gitignore, build scripts, etc.
* Moving source files from one directory or package to another

# How to report a bug
If you find a security vulnerability, do NOT open an issue. Email tvgamblin@gmail.com instead.

In order to determine whether you are dealing with a security issue, ask yourself these two questions:
* Can I access something that's not mine, or something I shouldn't have access to?
* Can I disable something for other people?

If the answer to either of those two questions are "yes", then you're probably dealing with a security issue. Note that even if you answer "no" to both questions, you may still be dealing with a security issue, so if you're unsure, just email us at security@travis-ci.org.

When filing an issue, make sure to answer these five questions:

1. What version of Python are you using?
2. What operating system and processor architecture are you using?
3. What did you do?
4. What did you expect to see?
5. What did you see instead?

If you're still not sure, contact threexc at tvgamblin@gmail.com


# How to suggest a feature or enhancement

Right now, the ANTS philosophy is to provide a simple, efficient user interface for running tests and collecting data on various WiFi devices. Over time, this will expand and change, but it is important that whatever is added is well-documented and modular.

If you find yourself wishing for a feature that doesn't exist in ANTS, you are probably not alone. Open an issue on our issues list on GitHub which describes the feature you would like to see, why you need it, and how it should work. Please keep in mind that the project is currently run primarily by masters and PhD students, so while we want to consider all potential additions, it may take some time before we can address a new feature request. The best way to get one in right now is to help by joining us in development.
