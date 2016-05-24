## -*- coding: utf-8 -*-
<%inherit file="base.mako"/>

<%def name="subject()" filter="n,trim">
    ${_('[mention]') if mention else ''} ${_('%(user)s commented on commit of %(repo_name)s') % {
                                         'user': h.person(user),
                                         'repo_name': repo_name
                                         } }
</%def>

<%def name="body_plaintext()" filter="n,trim">
${self.subject()}

* ${_('Comment link')}: ${commit_comment_url}

* ${_('Commit')}: ${h.show_id(commit)}

%if comment_file:
* ${_('File: %(comment_file)s on line %(comment_line)s') % {'comment_file': comment_file, 'comment_line': comment_line}}
%endif

---

${comment_body|n}


%if status_change:
    ${_('Commit status was changed to')}: *${status_change}*
%endif

</%def>


% if comment_file:
    <h4>${_('%(user)s commented on a file in commit of %(repo_url)s.') % {'user': h.person(user), 'repo_url': commit_target_repo} |n}</h4>
% else:
    <h4>${_('%(user)s commented on a commit of %(repo_url)s.') % {'user': h.person(user), 'repo_url': commit_target_repo} |n}</h4>
% endif

<ul>
    <li>${_('Comment link')}: <a href="${commit_comment_url}">${commit_comment_url}</a></li>
    %if comment_file:
        <li>${_('File: %(comment_file)s on line %(comment_line)s') % {'comment_file': comment_file, 'comment_line': comment_line}}</li>
    %endif
    <li>${_('Commit')}: ${h.show_id(commit)}</li>
    <li>
        ${_('Commit Description')}: <p>${h.urlify_commit_message(commit.message, repo_name)}</p>
    </li>
</ul>

<hr>
    <p>${h.render(comment_body, renderer=renderer_type, mentions=True)}</p>
<hr/>

%if status_change:
    <p>${_('Commit status was changed to')}: <b>${status_change}</b></p>
%endif
