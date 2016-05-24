## -*- coding: utf-8 -*-
<%inherit file="base.mako"/>

<%def name="subject()" filter="n,trim">
    ${_('%(user)s wants you to review pull request #%(pr_url)s: "%(pr_title)s"') % {
     'user': h.person(user),
     'pr_title': pull_request.title,
     'pr_url': pull_request.pull_request_id
     } |n}
</%def>


<%def name="body_plaintext()" filter="n,trim">
${self.subject()}


${h.literal(_('Pull request from %(source_ref_type)s:%(source_ref_name)s of %(repo_url)s into %(target_ref_type)s:%(target_ref_name)s') % {
   'source_ref_type': pull_request.source_ref_parts.type,
   'source_ref_name': pull_request.source_ref_parts.name,
   'target_ref_type': pull_request.target_ref_parts.type,
   'target_ref_name': pull_request.target_ref_parts.name,
   'repo_url': pull_request_source_repo_url
})}


* ${_('Link')}: ${pull_request_url}

* ${_('Title')}: ${pull_request.title}

* ${_('Description')}:

  ${pull_request.description}


* ${ungettext('Commit (%(num)s)', 'Commits (%(num)s)', len(pull_request_commits) ) % {'num': len(pull_request_commits)}}:

% for commit_id, message in pull_request_commits:
        - ${h.short_id(commit_id)}

        ${h.chop_at_smart(message, '\n', suffix_if_chopped='...')}
% endfor

</%def>


<h4>
${_('%(user)s wants you to review pull request #%(pr_id)s: "%(pr_title)s".') % {
 'user': h.person(user),
 'pr_title': pull_request.title,
 'pr_id': pull_request.pull_request_id
 } }
</h4>

<p>${h.literal(_('Pull request from %(source_ref_type)s:%(source_ref_name)s of %(repo_url)s into %(target_ref_type)s:%(target_ref_name)s') % {
   'source_ref_type': pull_request.source_ref_parts.type,
   'source_ref_name': pull_request.source_ref_parts.name,
   'target_ref_type': pull_request.target_ref_parts.type,
   'target_ref_name': pull_request.target_ref_parts.name,
   'repo_url': h.link_to(pull_request_source_repo.repo_name, pull_request_source_repo_url)
   })}
</p>

<p>${_('Link')}: ${h.link_to(pull_request_url, pull_request_url)}</p>

<p><strong>${_('Title')}</strong>: ${pull_request.title}</p>
<p>
    <strong>${_('Description')}:</strong><br/>
    <span style="white-space: pre-wrap;">${pull_request.description}</span>
</p>

<p>
    <strong>${ungettext('Commit (%(num)s)', 'Commits (%(num)s)', len(pull_request_commits) ) % {'num': len(pull_request_commits)}}</strong>:
    <ol>
    % for commit_id, message in pull_request_commits:
        <li>
            <pre>${h.short_id(commit_id)}</pre>
            ${h.chop_at_smart(message, '\n', suffix_if_chopped='...')}
        </li>
    % endfor
    </ol>
</p>
