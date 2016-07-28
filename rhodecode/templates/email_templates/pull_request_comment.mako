## -*- coding: utf-8 -*-
<%inherit file="base.mako"/>

<%def name="subject()" filter="n,trim">
${_('[mention]') if mention else ''} ${_('%(user)s commented on pull request #%(pr_id)s: "%(pr_title)s"') % {
                                     'user': h.person(user),
                                     'pr_title': pull_request.title,
                                     'pr_id': pull_request.pull_request_id
                                     } |n}
</%def>

<%def name="body_plaintext()" filter="n,trim">
${self.subject()}

* ${_('Comment link')}: ${pr_comment_url}

* ${_('Source repository')}: ${pr_source_repo_url}

%if comment_file:
* ${_('File: %(comment_file)s on line %(comment_line)s') % {'comment_file': comment_file, 'comment_line': comment_line}}
%endif

---

${comment_body|n}


%if status_change and not closing_pr:
   ${_('Pull request status was changed to')}: *${status_change}*
%elif status_change and closing_pr:
   ${_('Pull request was closed with status')}: *${status_change}*
%endif

${self.plaintext_footer()}
</%def>

<table style="text-align:left;vertical-align:middle;">
    <tr><td colspan="2" style="width:100%;padding-bottom:15px;border-bottom:1px solid #dbd9da;"><h4><a href="${pr_comment_url}" style="color:#427cc9;text-decoration:none;cursor:pointer">
% if comment_file:
    ${_('%(user)s commented on %(comment_file)s on pull request #%(pr_id)s: "%(pr_title)s".') % {'user': h.person(user), 'comment_file': comment_file, 'pr_title': pull_request.title, 'pr_id': pull_request.pull_request_id} |n}
% elif status_change and not closing_pr:
    ${_('%(user)s changed the status of pull request #%(pr_id)s "%(pr_title)s" to %(status)s.') % {'user': h.person(user),'pr_title': pull_request.title,'pr_id': pull_request.pull_request_id, 'status': status_change} |n}
%elif status_change and closing_pr:
    ${_('%(user)s closed pull request #%(pr_id)s "%(pr_title)s" with status %(status)s.') % {'user': h.person(user),'pr_title': pull_request.title,'pr_id': pull_request.pull_request_id, 'status': status_change} |n}
%else:
    ${_('%(user)s commented in pull request #%(pr_id)s "%(pr_title)s".') % {'user': h.person(user),'pr_title': pull_request.title,'pr_id': pull_request.pull_request_id} |n}
% endif
    </a></h4></td></tr>
    <tr><td style="padding-right:20px;padding-top:15px;">${_('Source')}</td><td style="padding-top:15px;"><a style="color:#427cc9;text-decoration:none;cursor:pointer" href="${pr_source_repo_url}">${pr_source_repo.repo_name}</a></td></tr>
    % if comment_file:
        <tr><td style="padding-right:20px;">${_('File')}</td><td>${_('%(comment_file)s on line %(comment_line)s') % {'comment_file': comment_file, 'comment_line': comment_line}}</td></tr>
    %endif
    %if status_change and not closing_pr:
       <tr><td style="padding-right:20px;">${_('Status')}</td><td>${_('The commit status was changed to')} ${status_change}</td></tr>
    %elif status_change and closing_pr:
       <tr><td style="padding-right:20px;">${_('Status')}</td><td>${_('Pull request was closed with status')}: ${status_change}</td></tr>
    %endif
    <tr><td style="padding-right:20px;">${_('Comment')}</td><td style="line-height:1.2em;">${h.render(comment_body, renderer=renderer_type, mentions=True)}</td></tr>
</table>

