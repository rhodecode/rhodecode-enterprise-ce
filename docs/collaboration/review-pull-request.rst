.. _review-requests-ref:

Review a |pr|
-------------

To review a pull request, use the following steps:

1. Open the review request from
   :menuselection:`Admin --> Repositories --> repo name --> Pull Requests --> Awaiting my review`
2. Leave your review comments inline, or in the commit message.
3. Set the review status from one of the following options:

   * :guilabel:`Not Reviewed`
   * :guilabel:`Approved`
   * :guilabel:`Approved & Closed`
   * :guilabel:`Rejected`
   * :guilabel:`Rejected & Closed`
   * :guilabel:`Under Review`

4. Select Comment

When the |pr| is approved by all reviewers you will be able to merge
automatically if |RCM| detects that it can do so safely. You will see this
message: `This pull request can be automatically merged.`

If rejected, you can fix the issues raised during review and then update the
|pr|.
