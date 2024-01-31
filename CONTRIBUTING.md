# How to contribute #

I'm really happy that you're interested in contributing to Temoa! Building a sustainable energy future with an open source energy system model takes a lot of effort, and we can use all the help we can get.

Here are some resources to help get you started:
* A [preprint](https://temoacloud.com/wp-content/uploads/2019/12/Hunter_etal_2013.pdf) of our Energy Economics paper laying out the motivation for our effort as well as the core model formulation.
* The [model documentation](https://temoacloud.com/docs/), which evolves with changes to the model formulation and the addition of new features.
* Use [our forum](https://groups.google.com/forum/#!forum/temoa-project) to ask questions about the model.

## Bugs and feature requests ##
If you would like to report a bug in the code or request a feature, please use our [Issue Tracker](https://github.com/TemoaProject/temoa/issues). If you're unsure or have questions, use [the forum](https://groups.google.com/forum/#!forum/). 

## Submitting Changes ##

To make changes to the code, first clone the repository. If you would like to share those changes back to our main repository, then you need to issue a pull request on GitHub. Details on how to contribute code are nicely outlined in [this blog post by Rob Allen](https://akrabat.com/the-beginners-guide-to-contributing-to-a-github-project/). If you'd like to make changes but don't feel comfortable with GitHub, get in touch with us through the [forum](https://groups.google.com/forum/#!forum/).

When making commits to the repository, please use verbose commit messages for all but the simplest changes. Every commit to the repository should include an appropriate summary message about the accompanying code changes.  Include enough context so that users get a high-level understanding of the changes without having to check the code.  For example, "Fixed broken algorithm" does not convey much information.  A more appropriate and complete summary message might be:

```
Add NEOS solve functionality to config file

With this commit, users can now use the NEOS server: https://neos-server.org/neos/ 
to solve their Temoa models. If users do not have a local install of cplex, this 
is a potentially faster option. Note that when using NEOS, both --neos and --solver 
must be used in the config file.
```

In general, we try to follow [these 7 rules](https://chris.beams.io/posts/git-commit/) when writing commit messages:

1. Separate subject from body with a blank line
2. Limit the subject line to 50 characters
3. Capitalize the subject line
4. Do not end the subject line with a period
5. Use the imperative mood in the subject line
6. Wrap the body at 72 characters
7. Use the body to explain what and why vs. how

Regarding how we format code, please see Chapter 7 of our user manual, which serves as the Temoa Code Style Guide. Be sure that all modified files included in the pull request have unix line endings.

Thanks,
Joe DeCarolis
NC State University