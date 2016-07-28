## -*- coding: utf-8 -*-
<%inherit file="base.mako"/>

<%def name="subject()" filter="n,trim">
${_('[mention]') if mention else ''} ${_('%(user)s commented on a commit of %(repo_name)s') % {
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

${self.plaintext_footer()}
</%def>

<table style="text-align:left;vertical-align:middle;">
    <tr><td colspan="2" style="width:100%;padding-bottom:15px;border-bottom:1px solid #dbd9da;"><h4><a href="${commit_comment_url}" style="color:#427cc9;text-decoration:none;cursor:pointer">
% if comment_file:
        ${_('%(user)s commented on %(comment_file)s on line %(comment_line)s</a> in the %(repo)s repository') % {'user': h.person(user), 'comment_file': comment_file, 'comment_line': comment_line, 'repo': commit_target_repo} |n}</h4>
% else:
        ${_('%(user)s commented on a commit</a> in the %(repo)s repository') % {'user': h.person(user), 'repo': commit_target_repo} |n}
% endif
    </h4></td></tr>
    <tr><td style="padding-right:20px;padding-top:15px;">${_('Commit')}</td><td style="padding-top:15px;"><a href="${commit_comment_url}" style="color:#427cc9;text-decoration:none;cursor:pointer">${h.show_id(commit)}</a></td></tr>
    <tr><td style="padding-right:20px;">${_('Description')}</td><td>${h.urlify_commit_message(commit.message, repo_name)}</td></tr>
    %if status_change:
        <tr><td style="padding-right:20px;">${_('Status')}<td/>${_('The commit status was changed to')} ${status_change}.</td></tr>
    %endif
    <tr><td style="padding-right:20px;">${_('Comment')}</td><td style="line-height:1.2em;">${h.render(comment_body, renderer=renderer_type, mentions=True)}</td></tr>
</table>