# CONTRIBUTING

## Introduction

This is the contribution guide for Teachable-dl. These guidelines apply to
both new issues and new pull requests. If you are making a pull request, please refer to
the [Pull request](#pull-requests) section, and if you are making an issue report, please
refer to the [Issue Report](#issues) section, as well as the
[Issue Report Template](ISSUE_TEMPLATE.md).

## Commenting

If you comment on an active pull request or issue report, make sure your comment is
concise and to the point. Comments on issue reports or pull requests should be relevant
and friendly, not attacks on the author or adages about something minimally relevant.
If you believe an issue report is not a "bug", please point out specifically and concisely your reasoning in a comment on the issue itself.

### Comment Guidelines

* Comments on Pull Requests and Issues should remain relevant to the subject in question and not derail discussions.
* Under no circumstances are users to be attacked for their ideas or contributions. All participants on a given PR or issue are expected to be civil. Failure to do so will result in disciplinary action.
* For more details, see the [Code of Conduct](../CODE_OF_CONDUCT.md).

## Issues

### Issue Guidelines

* Issue reports should be as detailed as possible, and if applicable, should include instructions on how to reproduce the bug.

## Pull requests

### Pull Request Guidelines

* Pull requests should be atomic; Make one commit for each distinct change, so if a part of a pull request needs to be removed/changed, you may simply modify that single commit. Due to limitations of the engine, this may not always be possible; but do try your best.

* Keep your pull requests small and reviewable whenever possible. Do not bundle unrelated fixes even if not bundling them generates more pull requests. 

* Document and explain your pull requests thoroughly. Failure to do so will delay a PR as we question why changes were made. Explaining with single comment on why you've made changes will help us review the PR faster and understand your decision making process.

* Pull requests should not have any merge commits except in the case of fixing merge conflicts for an existing pull request. New pull requests should not have any merge commits. Use `git rebase` or `git reset` to update your branches, not `git pull`.

* If your pull request is not finished make sure it is at least testable in a live environment.

* While we have no issue helping contributors (and especially new contributors) bring reasonably sized contributions up to standards via the pull request review process, larger contributions are expected to pass a higher bar of completeness and code quality *before* you open a pull request. Maintainers may close such pull requests that are deemed to be substantially flawed. You should take some time to discuss with maintainers or other contributors on how to improve the changes.
