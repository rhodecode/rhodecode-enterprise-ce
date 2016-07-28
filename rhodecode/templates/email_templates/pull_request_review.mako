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

${self.plaintext_footer()}
</%def>

<table style="text-align:left;vertical-align:middle;">
    <tr><td colspan="2" style="width:100%;padding-bottom:15px;border-bottom:1px solid #dbd9da;"><h4><a href="${pull_request_url}" style="color:#427cc9;text-decoration:none;cursor:pointer">${_('%(user)s wants you to review pull request #%(pr_id)s: "%(pr_title)s".') % { 'user': h.person(user), 'pr_title': pull_request.title, 'pr_id': pull_request.pull_request_id } }</a></h4></td></tr>
    <tr><td style="padding-right:20px;padding-top:15px;">${_('Title')}</td><td style="padding-top:15px;">${pull_request.title}</td></tr>
    <tr><td style="padding-right:20px;">${_('Source')}</td><td>${h.literal(_('<pre style="display:inline;border-radius:2px;color:#666666;font-size:12px;background-color:#f9f9f9;padding:.2em;border:1px solid #979797;">%(source_ref_name)s</pre> %(source_ref_type)s of %(source_repo_url)s') % {'source_ref_type': pull_request.source_ref_parts.type,'source_ref_name': pull_request.source_ref_parts.name,'source_repo_url': h.link_to(pull_request_source_repo.repo_name, pull_request_source_repo_url)})}</td></tr>
    <tr><td style="padding-right:20px;">${_('Target')}</td><td>${h.literal(_('<pre style="display:inline;border-radius:2px;color:#666666;font-size:12px;background-color:#f9f9f9;padding:.2em;border:1px solid #979797;">%(target_ref_name)s</pre> %(target_ref_type)s of %(target_repo_url)s') % {'target_ref_type': pull_request.target_ref_parts.type,'target_ref_name': pull_request.target_ref_parts.name,'target_repo_url': h.link_to(pull_request_target_repo.repo_name, pull_request_target_repo_url)})}</td></tr>
    <tr><td style="padding-right:20px;">${_('Description')}</td><td style="white-space:pre-wrap">${pull_request.description}</td></tr>
    <tr><td style="padding-right:20px;">${ungettext('%(num)s Commit', '%(num)s Commits', len(pull_request_commits)) % {'num': len(pull_request_commits)}}</td>
        <td><ol style="margin:0 0 0 1em;padding:0;text-align:left;">
% for commit_id, message in pull_request_commits:
<li style="margin:0 0 1em;"><pre style="margin:0 0 .5em">${h.short_id(commit_id)}</pre>
    ${h.chop_at_smart(message, '\n', suffix_if_chopped='...')}
</li>
% endfor
        </ol></td>
    </tr>
</table>
