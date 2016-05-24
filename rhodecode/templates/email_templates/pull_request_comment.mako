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

</%def>

% if comment_file:
    <h4>${_('%(user)s commented on a file on pull request #%(pr_id)s: "%(pr_title)s".') % {
            'user': h.person(user),
            'pr_title': pull_request.title,
            'pr_id': pull_request.pull_request_id
    } |n}</h4>
% else:
    <h4>${_('%(user)s commented on a pull request #%(pr_id)s "%(pr_title)s".') % {
            'user': h.person(user),
            'pr_title': pull_request.title,
            'pr_id': pull_request.pull_request_id
    } |n}</h4>
% endif

<ul>
    <li>${_('Comment link')}: <a href="${pr_comment_url}">${pr_comment_url}</a></li>
    <li>${_('Source repository')}: <a href="${pr_source_repo_url}">${pr_source_repo.repo_name}</a></li>
    %if comment_file:
        <li>${_('File: %(comment_file)s on line %(comment_line)s') % {'comment_file': comment_file, 'comment_line': comment_line}}</li>
    %endif
</ul>

<hr>
    <p>${h.render(comment_body, renderer=renderer_type, mentions=True)}</p>
<hr/>

%if status_change and not closing_pr:
   <p>${_('Pull request status was changed to')}: <b>${status_change}</b></p>
%elif status_change and closing_pr:
   <p>${_('Pull request was closed with status')}: <b>${status_change}</b></p>
%endif
